import uuid
import json
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template, Campaign, CampaignEmail
from app.templating import templates
from app.services.google_sheets import fetch_prospects
from app.services.variable_injection import render_template as render_vars
from app.services.scheduler import generate_send_times, schedule_campaign

router = APIRouter(prefix="/campaigns")


@router.get("/new/step1")
def wizard_step1(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse(request, "campaigns/wizard_step1.html", {
        "all_templates": all_templates,
    })


@router.post("/new/step1")
def wizard_step1_post(
    request: Request,
    campaign_name: str = Form(...),
    template_id: int = Form(...),
):
    request.session["wizard"] = {
        "campaign_name": campaign_name,
        "template_id": template_id,
    }
    return RedirectResponse(url="/campaigns/new/step2", status_code=303)


@router.get("/new/step2")
def wizard_step2(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    prospects = fetch_prospects()
    prospects = [p for p in prospects if p.get("email_du_decisionnaire", "").strip()]

    existing_emails = {
        row[0] for row in db.query(CampaignEmail.recipient_email).all()
    }
    available = [p for p in prospects if p["email_du_decisionnaire"] not in existing_emails]

    return templates.TemplateResponse(request, "campaigns/wizard_step2.html", {
        "prospects": available,
        "wizard": wizard,
    })


@router.post("/new/step2")
def wizard_step2_post(
    request: Request,
    selected_emails: list[str] = Form(default=[]),
    auto_select_count: int = Form(default=0),
    db: Session = Depends(get_db),
):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    prospects = fetch_prospects()
    prospects = [p for p in prospects if p.get("email_du_decisionnaire", "").strip()]
    existing_emails = {
        row[0] for row in db.query(CampaignEmail.recipient_email).all()
    }
    available = [p for p in prospects if p["email_du_decisionnaire"] not in existing_emails]

    if auto_select_count > 0:
        selected = available[:auto_select_count]
    else:
        selected = [p for p in available if p["email_du_decisionnaire"] in selected_emails]

    wizard["recipients"] = selected
    request.session["wizard"] = wizard
    return RedirectResponse(url="/campaigns/new/step3", status_code=303)


@router.get("/new/step3")
def wizard_step3(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard or "recipients" not in wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    template = db.get(Template, wizard["template_id"])
    previews = []
    for recipient in wizard["recipients"]:
        previews.append({
            "email": recipient["email_du_decisionnaire"],
            "nom": recipient.get("nom", ""),
            "prenom": recipient.get("prenom", ""),
            "subject": render_vars(template.subject_template, recipient),
            "body": render_vars(template.body_template, recipient),
        })

    return templates.TemplateResponse(request, "campaigns/wizard_step3.html", {
        "previews": previews,
        "wizard": wizard,
    })


@router.post("/new/step3")
def wizard_step3_post(request: Request):
    return RedirectResponse(url="/campaigns/new/step4", status_code=303)


@router.get("/new/step4")
def wizard_step4(request: Request):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    return templates.TemplateResponse(request, "campaigns/wizard_step4.html", {
        "wizard": wizard,
    })


@router.post("/new/step4")
def wizard_step4_post(
    request: Request,
    send_start_date: str = Form(...),
    send_start_time: str = Form("09:00"),
    send_end_date: str = Form(...),
    send_end_time: str = Form("18:00"),
):
    wizard = request.session.get("wizard", {})
    send_start = f"{send_start_date}T{send_start_time}"
    send_end = f"{send_end_date}T{send_end_time}"
    wizard["send_start"] = send_start
    wizard["send_end"] = send_end
    request.session["wizard"] = wizard
    return RedirectResponse(url="/campaigns/new/step5", status_code=303)


@router.get("/new/step5")
def wizard_step5(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard or "send_start" not in wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    template = db.get(Template, wizard["template_id"])
    return templates.TemplateResponse(request, "campaigns/wizard_step5.html", {
        "wizard": wizard,
        "template": template,
    })


@router.post("/new/confirm")
def wizard_confirm(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    send_start = datetime.fromisoformat(wizard["send_start"])
    send_end = datetime.fromisoformat(wizard["send_end"])

    campaign = Campaign(
        name=wizard["campaign_name"],
        template_id=wizard["template_id"],
        status="draft",
        send_start=send_start,
        send_end=send_end,
    )
    db.add(campaign)
    db.commit()

    template = db.get(Template, wizard["template_id"])
    recipients = wizard["recipients"]
    send_times = generate_send_times(len(recipients), send_start, send_end)

    for recipient, scheduled_at in zip(recipients, send_times):
        email = CampaignEmail(
            campaign_id=campaign.id,
            recipient_email=recipient["email_du_decisionnaire"],
            recipient_data=recipient,
            rendered_subject=render_vars(template.subject_template, recipient),
            rendered_body=render_vars(template.body_template, recipient),
            scheduled_at=scheduled_at,
            send_status="pending",
            tracking_id=str(uuid.uuid4()),
        )
        db.add(email)

    db.commit()

    schedule_campaign(db, campaign.id)

    request.session.pop("wizard", None)

    return RedirectResponse(url=f"/campaigns/{campaign.id}", status_code=303)


@router.get("/{campaign_id}")
def campaign_detail(campaign_id: int, request: Request, db: Session = Depends(get_db)):
    campaign = db.get(Campaign, campaign_id)
    emails = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.campaign_id == campaign_id)
        .order_by(CampaignEmail.scheduled_at)
        .all()
    )

    total = len(emails)
    sent = sum(1 for e in emails if e.send_status == "sent")
    opened = sum(1 for e in emails if e.opened_at is not None)
    replied = sum(1 for e in emails if e.reply_detected_at is not None)

    return templates.TemplateResponse(request, "campaigns/detail.html", {
        "campaign": campaign,
        "emails": emails,
        "total": total,
        "sent": sent,
        "opened": opened,
        "replied": replied,
    })

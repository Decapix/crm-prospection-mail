import uuid
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template, Campaign, CampaignEmail
from app.templating import templates

router = APIRouter(prefix="/admin")


@router.get("/import")
def import_page(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse(request, "admin/import.html", {
        "all_templates": all_templates,
    })


@router.post("/import")
def import_campaign(
    request: Request,
    campaign_name: str = Form(...),
    template_id: int = Form(...),
    status: str = Form("completed"),
    emails: str = Form(...),
    send_status: str = Form("sent"),
    sent_date: str = Form(""),
    sent_time: str = Form("10:00"),
    db: Session = Depends(get_db),
):
    sent_at = None
    if sent_date:
        sent_at = datetime.fromisoformat(f"{sent_date}T{sent_time}")

    campaign = Campaign(
        name=campaign_name,
        template_id=template_id,
        status=status,
        send_start=sent_at,
        send_end=sent_at,
    )
    db.add(campaign)
    db.commit()

    email_list = [e.strip() for e in emails.strip().split("\n") if e.strip()]

    for email_addr in email_list:
        ce = CampaignEmail(
            campaign_id=campaign.id,
            recipient_email=email_addr,
            recipient_data={},
            rendered_subject="(imported)",
            rendered_body="(imported)",
            scheduled_at=sent_at,
            sent_at=sent_at,
            send_status=send_status,
            tracking_id=str(uuid.uuid4()),
        )
        db.add(ce)

    db.commit()
    return RedirectResponse(url=f"/campaigns/{campaign.id}", status_code=303)

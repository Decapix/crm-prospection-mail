from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template
from app.templating import templates

router = APIRouter(prefix="/templates")


@router.get("")
def list_templates(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()

    template_stats = []
    for t in all_templates:
        campaign_count = len(t.campaigns)
        all_emails = []
        for c in t.campaigns:
            all_emails.extend(c.emails)

        sent = sum(1 for e in all_emails if e.send_status == "sent")
        opened = sum(1 for e in all_emails if e.opened_at is not None)
        replied = sum(1 for e in all_emails if e.reply_detected_at is not None)
        open_rate = round(opened / sent * 100, 1) if sent > 0 else 0
        reply_rate = round(replied / sent * 100, 1) if sent > 0 else 0

        template_stats.append({
            "template": t,
            "campaign_count": campaign_count,
            "sent": sent,
            "open_rate": open_rate,
            "reply_rate": reply_rate,
        })

    return templates.TemplateResponse(request, "email_templates/list.html", {
        "template_stats": template_stats,
    })


@router.get("/create")
def create_template_form(request: Request):
    return templates.TemplateResponse(request, "email_templates/create.html", {})


@router.post("/create")
def create_template(
    request: Request,
    name: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    db: Session = Depends(get_db),
):
    template = Template(
        name=name,
        subject_template=subject_template,
        body_template=body_template,
    )
    db.add(template)
    db.commit()
    return RedirectResponse(url="/templates", status_code=303)


@router.get("/{template_id}/edit")
def edit_template_form(template_id: int, request: Request, db: Session = Depends(get_db)):
    template = db.query(Template).get(template_id)
    return templates.TemplateResponse(request, "email_templates/edit.html", {
        "template": template,
    })


@router.post("/{template_id}/edit")
def edit_template(
    template_id: int,
    request: Request,
    name: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    db: Session = Depends(get_db),
):
    template = db.query(Template).get(template_id)
    template.name = name
    template.subject_template = subject_template
    template.body_template = body_template
    db.commit()
    return RedirectResponse(url="/templates", status_code=303)

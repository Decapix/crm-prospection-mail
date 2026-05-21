from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CampaignEmail, FollowUp
from app.templating import templates

router = APIRouter(prefix="/replies")


@router.get("")
def replies_list(request: Request, db: Session = Depends(get_db)):
    replied_emails = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.reply_detected_at.isnot(None))
        .order_by(CampaignEmail.reply_detected_at.desc())
        .all()
    )

    return templates.TemplateResponse(request, "replies/list.html", {
        "replied_emails": replied_emails,
    })


@router.get("/{campaign_email_id}")
def prospect_detail(campaign_email_id: int, request: Request, db: Session = Depends(get_db)):
    email = db.get(CampaignEmail, campaign_email_id)
    follow_ups = (
        db.query(FollowUp)
        .filter(FollowUp.campaign_email_id == campaign_email_id)
        .order_by(FollowUp.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(request, "replies/detail.html", {
        "email": email,
        "follow_ups": follow_ups,
    })


@router.post("/{campaign_email_id}/follow-up")
def add_follow_up(
    campaign_email_id: int,
    note: str = Form(...),
    db: Session = Depends(get_db),
):
    follow_up = FollowUp(
        campaign_email_id=campaign_email_id,
        note=note,
    )
    db.add(follow_up)
    db.commit()
    return RedirectResponse(url=f"/replies/{campaign_email_id}", status_code=303)

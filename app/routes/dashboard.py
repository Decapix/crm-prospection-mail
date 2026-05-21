from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign
from app.templating import templates

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()

    campaign_stats = []
    for c in campaigns:
        total = len(c.emails)
        sent = sum(1 for e in c.emails if e.send_status == "sent")
        opened = sum(1 for e in c.emails if e.opened_at is not None)
        replied = sum(1 for e in c.emails if e.reply_detected_at is not None)
        open_rate = round(opened / sent * 100, 1) if sent > 0 else 0
        reply_rate = round(replied / sent * 100, 1) if sent > 0 else 0

        campaign_stats.append({
            "campaign": c,
            "total": total,
            "sent": sent,
            "open_rate": open_rate,
            "reply_rate": reply_rate,
        })

    return templates.TemplateResponse(request, "dashboard.html", {
        "campaign_stats": campaign_stats,
    })

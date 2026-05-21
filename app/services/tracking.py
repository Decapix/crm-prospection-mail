from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CampaignEmail


def build_tracking_url(tracking_id: str, server_url: str) -> str:
    return f"{server_url}/penda/{tracking_id}"


def record_open(db: Session, tracking_id: str) -> dict | None:
    """Record an email open. Returns info dict or None if tracking_id not found."""
    email = db.query(CampaignEmail).filter(CampaignEmail.tracking_id == tracking_id).first()
    if email is None:
        return None

    first_open = email.opened_at is None
    email.opened_at = datetime.utcnow()
    db.commit()

    return {
        "first_open": first_open,
        "recipient_email": email.recipient_email,
        "recipient_data": email.recipient_data,
        "campaign_name": email.campaign.name,
        "campaign_email_id": email.id,
    }

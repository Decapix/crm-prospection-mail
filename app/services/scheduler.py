import random
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from sqlalchemy.orm import Session

from app.config import settings
from app.models import CampaignEmail, Campaign

logger = logging.getLogger(__name__)

scheduler: BackgroundScheduler | None = None


def generate_send_times(
    count: int, start: datetime, end: datetime
) -> list[datetime]:
    """Generate `count` random datetimes between start and end, sorted."""
    delta = (end - start).total_seconds()
    times = []
    for _ in range(count):
        offset = random.random() * delta
        t = start + timedelta(seconds=offset)
        times.append(t)
    times.sort()
    return times


def send_single_email(campaign_email_id: int) -> None:
    """Send a single campaign email. Called by APScheduler at scheduled time."""
    from app.database import SessionLocal
    from app.services.gmail import send_email

    db = SessionLocal()
    try:
        email = db.query(CampaignEmail).get(campaign_email_id)
        if email is None or email.send_status != "pending":
            return

        try:
            gmail_id = send_email(
                to=email.recipient_email,
                subject=email.rendered_subject,
                html_body=email.rendered_body,
                tracking_id=email.tracking_id,
            )
            email.gmail_message_id = gmail_id
            email.sent_at = datetime.utcnow()
            email.send_status = "sent"
            logger.info(f"Sent email to {email.recipient_email}")
        except Exception as e:
            email.send_status = "failed"
            email.failure_reason = str(e)
            logger.error(f"Failed to send to {email.recipient_email}: {e}")

        db.commit()

        campaign = email.campaign
        pending_count = (
            db.query(CampaignEmail)
            .filter(
                CampaignEmail.campaign_id == campaign.id,
                CampaignEmail.send_status == "pending",
            )
            .count()
        )
        if pending_count == 0:
            campaign.status = "completed"
            db.commit()
            logger.info(f"Campaign '{campaign.name}' completed")
    finally:
        db.close()


def schedule_campaign(db: Session, campaign_id: int) -> None:
    """Schedule all pending emails for a campaign."""
    global scheduler
    if scheduler is None:
        return

    campaign = db.query(Campaign).get(campaign_id)
    if campaign is None:
        return

    pending_emails = (
        db.query(CampaignEmail)
        .filter(
            CampaignEmail.campaign_id == campaign_id,
            CampaignEmail.send_status == "pending",
        )
        .all()
    )

    for email in pending_emails:
        if email.scheduled_at is None:
            continue
        scheduler.add_job(
            send_single_email,
            "date",
            run_date=email.scheduled_at,
            args=[email.id],
            id=f"send_email_{email.id}",
            replace_existing=True,
        )

    campaign.status = "scheduled"
    db.commit()
    logger.info(
        f"Scheduled {len(pending_emails)} emails for campaign '{campaign.name}'"
    )


def reload_pending_jobs(db: Session) -> None:
    """Reload all pending email jobs on startup."""
    pending_emails = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.send_status == "pending")
        .all()
    )

    now = datetime.utcnow()
    for email in pending_emails:
        if email.scheduled_at is None:
            continue
        if email.scheduled_at <= now:
            send_single_email(email.id)
        else:
            schedule_campaign(db, email.campaign_id)
            break


def check_replies_job() -> None:
    """Periodic job to check Gmail for replies to sent campaign emails."""
    from app.database import SessionLocal
    from app.services.gmail import check_for_replies

    db = SessionLocal()
    try:
        sent_emails = (
            db.query(CampaignEmail)
            .filter(
                CampaignEmail.send_status == "sent",
                CampaignEmail.gmail_message_id.isnot(None),
                CampaignEmail.reply_detected_at.is_(None),
            )
            .all()
        )

        if not sent_emails:
            return

        msg_id_to_email = {e.gmail_message_id: e for e in sent_emails}
        results = check_for_replies(list(msg_id_to_email.keys()))

        for msg_id, has_reply in results.items():
            if has_reply:
                email = msg_id_to_email[msg_id]
                email.reply_detected_at = datetime.utcnow()
                logger.info(f"Reply detected from {email.recipient_email}")

        db.commit()
    finally:
        db.close()


def init_scheduler() -> BackgroundScheduler:
    """Initialize and start the APScheduler."""
    global scheduler
    job_store = SQLAlchemyJobStore(url=settings.database_url)
    scheduler = BackgroundScheduler(jobstores={"default": job_store})
    scheduler.start()
    scheduler.add_job(
        check_replies_job,
        "interval",
        minutes=5,
        id="check_replies",
        replace_existing=True,
    )
    return scheduler


def shutdown_scheduler() -> None:
    """Shut down the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None

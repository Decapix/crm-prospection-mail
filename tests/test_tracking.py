from datetime import datetime

from app.models import Template, Campaign, CampaignEmail
from app.services.tracking import record_open, build_tracking_url


def test_build_tracking_url():
    url = build_tracking_url("abc-123", "https://my-server.com")
    assert url == "https://my-server.com/penda/abc-123"


def test_record_open_first_time(db_session):
    template = Template(name="T", subject_template="S", body_template="B")
    db_session.add(template)
    db_session.commit()

    campaign = Campaign(
        name="C1", template_id=template.id, status="in_progress",
        send_start=datetime(2026, 6, 1, 9, 0), send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    email = CampaignEmail(
        campaign_id=campaign.id, recipient_email="test@example.com",
        recipient_data={"prenom": "Jean"}, rendered_subject="S", rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0), send_status="sent", tracking_id="track-001",
    )
    db_session.add(email)
    db_session.commit()

    result = record_open(db_session, "track-001")
    assert result is not None
    assert result["first_open"] is True
    assert result["recipient_email"] == "test@example.com"
    assert result["recipient_data"]["prenom"] == "Jean"
    assert result["campaign_name"] == "C1"

    refreshed = db_session.query(CampaignEmail).filter_by(tracking_id="track-001").first()
    assert refreshed.opened_at is not None


def test_record_open_second_time(db_session):
    template = Template(name="T", subject_template="S", body_template="B")
    db_session.add(template)
    db_session.commit()

    campaign = Campaign(
        name="C1", template_id=template.id, status="in_progress",
        send_start=datetime(2026, 6, 1, 9, 0), send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    email = CampaignEmail(
        campaign_id=campaign.id, recipient_email="test@example.com",
        recipient_data={}, rendered_subject="S", rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0), send_status="sent",
        tracking_id="track-002", opened_at=datetime(2026, 6, 1, 11, 0),
    )
    db_session.add(email)
    db_session.commit()

    result = record_open(db_session, "track-002")
    assert result is not None
    assert result["first_open"] is False


def test_record_open_unknown_tracking_id(db_session):
    result = record_open(db_session, "nonexistent")
    assert result is None

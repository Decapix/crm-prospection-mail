from datetime import datetime

from app.models import Template, Campaign, CampaignEmail, FollowUp


def test_create_template(db_session):
    template = Template(
        name="Test Template",
        subject_template="Hello {{prenom}}",
        body_template="<p>Bonjour {{prenom}}</p>",
    )
    db_session.add(template)
    db_session.commit()

    result = db_session.query(Template).first()
    assert result.name == "Test Template"
    assert result.subject_template == "Hello {{prenom}}"
    assert result.created_at is not None


def test_create_campaign_with_template(db_session):
    template = Template(
        name="T1",
        subject_template="Sub",
        body_template="Body",
    )
    db_session.add(template)
    db_session.commit()

    campaign = Campaign(
        name="Campaign 1",
        template_id=template.id,
        status="draft",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    result = db_session.query(Campaign).first()
    assert result.name == "Campaign 1"
    assert result.template.name == "T1"
    assert result.status == "draft"


def test_create_campaign_email(db_session):
    template = Template(name="T", subject_template="S", body_template="B")
    db_session.add(template)
    db_session.commit()

    campaign = Campaign(
        name="C1",
        template_id=template.id,
        status="scheduled",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    email = CampaignEmail(
        campaign_id=campaign.id,
        recipient_email="test@example.com",
        recipient_data={"prenom": "Jean", "nom": "Dupont"},
        rendered_subject="Hello Jean",
        rendered_body="<p>Bonjour Jean</p>",
        scheduled_at=datetime(2026, 6, 1, 10, 30),
        send_status="pending",
        tracking_id="abc-123",
    )
    db_session.add(email)
    db_session.commit()

    result = db_session.query(CampaignEmail).first()
    assert result.recipient_email == "test@example.com"
    assert result.recipient_data["prenom"] == "Jean"
    assert result.send_status == "pending"
    assert result.opened_at is None
    assert result.campaign.name == "C1"


def test_create_follow_up(db_session):
    template = Template(name="T", subject_template="S", body_template="B")
    db_session.add(template)
    db_session.commit()

    campaign = Campaign(
        name="C1",
        template_id=template.id,
        status="completed",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    email = CampaignEmail(
        campaign_id=campaign.id,
        recipient_email="test@example.com",
        recipient_data={},
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="xyz-789",
    )
    db_session.add(email)
    db_session.commit()

    follow_up = FollowUp(
        campaign_email_id=email.id,
        note="Already called, waiting for callback",
    )
    db_session.add(follow_up)
    db_session.commit()

    result = db_session.query(FollowUp).first()
    assert result.note == "Already called, waiting for callback"
    assert result.campaign_email.recipient_email == "test@example.com"
    assert result.created_at is not None

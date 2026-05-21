from datetime import datetime
from unittest.mock import patch

from tests.conftest import TestSession, client
from app.models import Template, Campaign, CampaignEmail


def test_wizard_step1_shows_templates():
    db = TestSession()
    db.add(Template(name="T1", subject_template="S", body_template="B"))
    db.commit()
    db.close()

    response = client.get("/campaigns/new/step1")
    assert response.status_code == 200
    assert "T1" in response.text


def test_wizard_step1_post():
    db = TestSession()
    t = Template(name="T1", subject_template="S", body_template="B")
    db.add(t)
    db.commit()
    tid = t.id
    db.close()

    response = client.post("/campaigns/new/step1", data={
        "campaign_name": "My Campaign",
        "template_id": str(tid),
    }, follow_redirects=False)
    assert response.status_code == 303
    assert "/campaigns/new/step2" in response.headers["location"]


@patch("app.routes.campaigns.fetch_prospects")
def test_wizard_step2_shows_available_emails(mock_fetch):
    mock_fetch.return_value = [
        {"nom": "A", "prenom": "Jean", "email_du_decisionnaire": "jean@a.com"},
        {"nom": "B", "prenom": "Paul", "email_du_decisionnaire": "paul@b.com"},
        {"nom": "C", "prenom": "", "email_du_decisionnaire": ""},
    ]

    db = TestSession()
    t = Template(name="T1", subject_template="S", body_template="B")
    db.add(t)
    db.commit()
    tid = t.id
    db.close()

    # Go through step 1 to set session
    client.post("/campaigns/new/step1", data={
        "campaign_name": "Test",
        "template_id": str(tid),
    }, follow_redirects=False)

    response = client.get("/campaigns/new/step2")
    assert response.status_code == 200
    assert "jean@a.com" in response.text
    assert "paul@b.com" in response.text


def test_campaign_detail():
    db = TestSession()
    t = Template(name="T1", subject_template="S", body_template="B")
    db.add(t)
    db.commit()

    c = Campaign(
        name="C1", template_id=t.id, status="completed",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(c)
    db.commit()

    e = CampaignEmail(
        campaign_id=c.id, recipient_email="test@test.com",
        recipient_data={"prenom": "Test"}, rendered_subject="S", rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0), send_status="sent",
        tracking_id="t-100", sent_at=datetime(2026, 6, 1, 10, 5),
    )
    db.add(e)
    db.commit()
    cid = c.id
    db.close()

    response = client.get(f"/campaigns/{cid}")
    assert response.status_code == 200
    assert "test@test.com" in response.text

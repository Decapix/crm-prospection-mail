"""Smoke test: verify all pages load without errors."""

from datetime import datetime

from tests.conftest import TestSession, client
from app.models import Template, Campaign, CampaignEmail, FollowUp


def _seed_data():
    db = TestSession()
    t = Template(name="T1", subject_template="Hi {{prenom}}", body_template="<p>Hello</p>")
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
        recipient_data={"prenom": "Jean", "nom": "TestCo", "telephone": "0600000000"},
        rendered_subject="Hi Jean", rendered_body="<p>Hello</p>",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent", tracking_id="smoke-001",
        sent_at=datetime(2026, 6, 1, 10, 5),
        reply_detected_at=datetime(2026, 6, 1, 14, 0),
    )
    db.add(e)
    db.commit()

    fu = FollowUp(campaign_email_id=e.id, note="Called")
    db.add(fu)
    db.commit()

    result = {"template_id": t.id, "campaign_id": c.id, "email_id": e.id}
    db.close()
    return result


def test_all_pages_load():
    ids = _seed_data()

    pages = [
        "/",
        "/templates",
        "/templates/create",
        f"/templates/{ids['template_id']}/edit",
        "/campaigns/new/step1",
        f"/campaigns/{ids['campaign_id']}",
        "/replies",
        f"/replies/{ids['email_id']}",
        "/admin/import",
    ]

    for page in pages:
        response = client.get(page)
        assert response.status_code == 200, f"Page {page} returned {response.status_code}"

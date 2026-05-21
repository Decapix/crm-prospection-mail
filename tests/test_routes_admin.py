from tests.conftest import TestSession, client
from app.models import Template, Campaign, CampaignEmail


def test_import_page():
    response = client.get("/admin/import")
    assert response.status_code == 200
    assert "Import" in response.text


def test_import_campaign():
    db = TestSession()
    t = Template(name="Manual Template", subject_template="S", body_template="B")
    db.add(t)
    db.commit()
    tid = t.id
    db.close()

    response = client.post("/admin/import", data={
        "campaign_name": "Manual Campaign",
        "template_id": str(tid),
        "status": "completed",
        "emails": "test1@example.com\ntest2@example.com",
        "send_status": "sent",
        "sent_date": "2026-05-01T10:00",
    }, follow_redirects=False)
    assert response.status_code == 303

    db2 = TestSession()
    campaign = db2.query(Campaign).first()
    assert campaign is not None
    assert campaign.name == "Manual Campaign"
    assert campaign.status == "completed"

    emails = db2.query(CampaignEmail).all()
    assert len(emails) == 2
    assert emails[0].recipient_email == "test1@example.com"
    assert emails[0].send_status == "sent"
    db2.close()

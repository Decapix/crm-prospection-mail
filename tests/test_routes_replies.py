from datetime import datetime

from tests.conftest import TestSession, client
from app.models import Template, Campaign, CampaignEmail, FollowUp


def _create_replied_email(db):
    t = Template(name="T", subject_template="S", body_template="B")
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
        campaign_id=c.id, recipient_email="hugues@123syndic.com",
        recipient_data={
            "nom": "123syndic", "prenom": "Hugues",
            "nom_du_fondateur_decisionnaire": "Hugues Blondet",
            "telephone": "06 63 82 09 47",
            "email_du_decisionnaire": "hugues@123syndic.com",
        },
        rendered_subject="S", rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0), send_status="sent",
        tracking_id="r-001", sent_at=datetime(2026, 6, 1, 10, 5),
        reply_detected_at=datetime(2026, 6, 1, 14, 0),
    )
    db.add(e)
    db.commit()
    return e


def test_replies_list():
    db = TestSession()
    _create_replied_email(db)
    db.close()

    response = client.get("/replies")
    assert response.status_code == 200
    assert "hugues@123syndic.com" in response.text
    assert "123syndic" in response.text


def test_replies_list_empty():
    response = client.get("/replies")
    assert response.status_code == 200


def test_prospect_detail():
    db = TestSession()
    e = _create_replied_email(db)
    eid = e.id
    db.close()

    response = client.get(f"/replies/{eid}")
    assert response.status_code == 200
    assert "Hugues Blondet" in response.text
    assert "06 63 82 09 47" in response.text


def test_add_follow_up():
    db = TestSession()
    e = _create_replied_email(db)
    eid = e.id
    db.close()

    response = client.post(f"/replies/{eid}/follow-up", data={
        "note": "Called, no answer",
    }, follow_redirects=False)
    assert response.status_code == 303

    db2 = TestSession()
    follow_ups = db2.query(FollowUp).filter_by(campaign_email_id=eid).all()
    assert len(follow_ups) == 1
    assert follow_ups[0].note == "Called, no answer"
    db2.close()

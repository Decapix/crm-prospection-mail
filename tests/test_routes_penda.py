from datetime import datetime
from unittest.mock import patch, AsyncMock

from tests.conftest import TestSession, client
from app.models import Template, Campaign, CampaignEmail


@patch("app.routes.penda.send_notification", new_callable=AsyncMock)
@patch("app.routes.penda.format_open_notification", return_value="test notification")
def test_penda_returns_pixel_and_records_open(mock_format, mock_send):
    db = TestSession()
    t = Template(name="T", subject_template="S", body_template="B")
    db.add(t)
    db.commit()

    c = Campaign(
        name="C1", template_id=t.id, status="in_progress",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(c)
    db.commit()

    e = CampaignEmail(
        campaign_id=c.id, recipient_email="test@test.com",
        recipient_data={"prenom": "Test", "nom": "Co"},
        rendered_subject="S", rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent", tracking_id="penda-001",
    )
    db.add(e)
    db.commit()
    db.close()

    response = client.get("/penda/penda-001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"

    db2 = TestSession()
    updated = db2.query(CampaignEmail).filter_by(tracking_id="penda-001").first()
    assert updated.opened_at is not None
    db2.close()


def test_penda_unknown_tracking_id():
    response = client.get("/penda/nonexistent")
    assert response.status_code == 200

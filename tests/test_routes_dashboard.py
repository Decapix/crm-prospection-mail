from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool


engine_test = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSession = sessionmaker(bind=engine_test)


def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def setup_function():
    Base.metadata.create_all(bind=engine_test)


def teardown_function():
    Base.metadata.drop_all(bind=engine_test)


def test_dashboard_empty():
    response = client.get("/")
    assert response.status_code == 200
    assert "Campagnes" in response.text


def test_dashboard_with_campaign():
    db = TestSession()
    template = Template(name="T1", subject_template="S", body_template="B")
    db.add(template)
    db.commit()

    campaign = Campaign(
        name="Test Campaign",
        template_id=template.id,
        status="completed",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(campaign)
    db.commit()

    email = CampaignEmail(
        campaign_id=campaign.id,
        recipient_email="test@example.com",
        recipient_data={},
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="t-001",
        opened_at=datetime(2026, 6, 1, 12, 0),
    )
    db.add(email)
    db.commit()
    db.close()

    response = client.get("/")
    assert response.status_code == 200
    assert "Test Campaign" in response.text

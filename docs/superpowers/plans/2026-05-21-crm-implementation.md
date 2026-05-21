# CRM Prospection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a self-hosted prospection CRM with campaign management, email tracking, Telegram notifications, and follow-up tracking.

**Architecture:** Single FastAPI application serving Jinja2 HTML pages and API endpoints. SQLite database via SQLAlchemy. APScheduler for deferred email sending. Google APIs for Sheets and Gmail. Telegram Bot API for open notifications.

**Tech Stack:** FastAPI, Jinja2, SQLAlchemy, SQLite, APScheduler, google-api-python-client, httpx (for Telegram), uvicorn, Docker

**Spec:** `docs/superpowers/specs/2026-05-21-crm-design.md`

---

## File Structure

```
crm/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app factory, lifespan, static/template config
│   ├── config.py                  # Pydantic Settings from .env
│   ├── database.py                # SQLAlchemy engine, session, Base
│   ├── models.py                  # ORM models: Template, Campaign, CampaignEmail, FollowUp
│   ├── services/
│   │   ├── __init__.py
│   │   ├── google_sheets.py       # Fetch prospects from Google Sheet
│   │   ├── gmail.py               # Send email, get thread replies
│   │   ├── scheduler.py           # APScheduler setup, schedule/send campaign emails
│   │   ├── tracking.py            # Record opens, build tracking pixel URL
│   │   └── telegram.py            # Send Telegram notification
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── dashboard.py           # GET / — campaign summary
│   │   ├── campaigns.py           # Campaign wizard (5 steps) + detail
│   │   ├── templates_routes.py    # Template CRUD + stats
│   │   ├── replies.py             # Replies list + prospect detail + follow-ups
│   │   ├── admin.py               # Manual import page
│   │   └── penda.py               # GET /penda/{tracking_id} — tracking pixel
│   └── templates/
│       ├── base.html
│       ├── dashboard.html
│       ├── campaigns/
│       │   ├── detail.html
│       │   ├── wizard_step1.html
│       │   ├── wizard_step2.html
│       │   ├── wizard_step3.html
│       │   ├── wizard_step4.html
│       │   └── wizard_step5.html
│       ├── email_templates/
│       │   ├── list.html
│       │   ├── create.html
│       │   └── edit.html
│       ├── replies/
│       │   ├── list.html
│       │   └── detail.html
│       └── admin/
│           └── import.html
├── static/
│   └── style.css
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test DB session, test client fixtures
│   ├── test_models.py
│   ├── test_tracking.py
│   ├── test_telegram.py
│   ├── test_variable_injection.py
│   ├── test_scheduler.py
│   ├── test_routes_templates.py
│   ├── test_routes_campaigns.py
│   ├── test_routes_dashboard.py
│   ├── test_routes_replies.py
│   ├── test_routes_admin.py
│   └── test_routes_penda.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── .gitignore
```

Note: Jinja2 template directory is `app/templates/` but the email templates (subject/body with variables) are stored in the DB table `templates`. To avoid naming confusion, the Jinja2 HTML files for the template CRUD pages live under `app/templates/email_templates/` and the route file is `templates_routes.py`.

---

### Task 1: Project Scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `app/__init__.py`
- Create: `app/config.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy==2.0.35
jinja2==3.1.4
python-multipart==0.0.12
apscheduler==3.10.4
google-api-python-client==2.149.0
google-auth-oauthlib==1.2.1
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
httpx==0.27.2
```

- [ ] **Step 2: Create .env.example**

```
# Google API
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
GOOGLE_TOKEN_PATH=credentials/token.json
GOOGLE_SHEET_ID=your-sheet-id-here

# Gmail
GMAIL_SENDER_ADDRESS=your@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Server
SERVER_URL=http://localhost:8000

# Database
DATABASE_URL=sqlite:///./data/crm.db
```

- [ ] **Step 3: Create .gitignore**

```
__pycache__/
*.pyc
.env
credentials/
data/
*.db
venv/
.pytest_cache/
```

- [ ] **Step 4: Create app/__init__.py and tests/__init__.py**

Both empty files.

- [ ] **Step 5: Create app/config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_credentials_path: str = "credentials/google_credentials.json"
    google_token_path: str = "credentials/token.json"
    google_sheet_id: str = ""

    gmail_sender_address: str = ""

    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

    server_url: str = "http://localhost:8000"

    database_url: str = "sqlite:///./data/crm.db"

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 6: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data /app/credentials

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 7: Create docker-compose.yml**

```yaml
services:
  crm:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - crm_data:/app/data
      - ./credentials:/app/credentials:ro
    env_file:
      - .env
    restart: unless-stopped

volumes:
  crm_data:
```

- [ ] **Step 8: Add pydantic-settings to requirements.txt**

Add `pydantic-settings==2.5.2` to `requirements.txt` (needed by config.py).

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: project scaffolding — requirements, config, Docker setup"
```

---

### Task 2: Database & Models

**Files:**
- Create: `app/database.py`
- Create: `app/models.py`
- Create: `tests/conftest.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing test**

Create `tests/conftest.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()
```

Create `tests/test_models.py`:

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL — `app.database` and `app.models` do not exist yet.

- [ ] **Step 3: Create app/database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 4: Create app/models.py**

```python
import json
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import TypeDecorator

from app.database import Base


class JSONType(TypeDecorator):
    """Store Python dicts as JSON strings in SQLite."""

    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    subject_template = Column(Text, nullable=False)
    body_template = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    campaigns = relationship("Campaign", back_populates="template")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")
    send_start = Column(DateTime, nullable=True)
    send_end = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())

    template = relationship("Template", back_populates="campaigns")
    emails = relationship("CampaignEmail", back_populates="campaign")


class CampaignEmail(Base):
    __tablename__ = "campaign_emails"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=False)
    recipient_email = Column(String, nullable=False)
    recipient_data = Column(JSONType, nullable=False)
    rendered_subject = Column(Text, nullable=False)
    rendered_body = Column(Text, nullable=False)
    scheduled_at = Column(DateTime, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    send_status = Column(String, nullable=False, default="pending")
    failure_reason = Column(Text, nullable=True)
    tracking_id = Column(String, unique=True, nullable=False)
    gmail_message_id = Column(String, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    reply_detected_at = Column(DateTime, nullable=True)

    campaign = relationship("Campaign", back_populates="emails")
    follow_ups = relationship("FollowUp", back_populates="campaign_email")


class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_email_id = Column(
        Integer, ForeignKey("campaign_emails.id"), nullable=False
    )
    note = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    campaign_email = relationship("CampaignEmail", back_populates="follow_ups")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_models.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/database.py app/models.py tests/conftest.py tests/test_models.py tests/__init__.py
git commit -m "feat: database setup and ORM models"
```

---

### Task 3: Variable Injection Service

**Files:**
- Create: `app/services/__init__.py`
- Create: `app/services/variable_injection.py`
- Create: `tests/test_variable_injection.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_variable_injection.py`:

```python
from app.services.variable_injection import render_template, normalize_column_name


def test_normalize_column_name():
    assert normalize_column_name("nom") == "nom"
    assert normalize_column_name("nom du fondateur/decisionnaire") == "nom_du_fondateur_decisionnaire"
    assert normalize_column_name("email du decisionnaire") == "email_du_decisionnaire"
    assert normalize_column_name("site_web") == "site_web"
    assert normalize_column_name("linkedlin du fondateur/decisionnaire") == "linkedlin_du_fondateur_decisionnaire"


def test_render_template_simple():
    template = "Bonjour {{prenom}}, bienvenue chez {{nom}}"
    data = {"prenom": "Hugues", "nom": "123syndic"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, bienvenue chez 123syndic"


def test_render_template_with_normalized_keys():
    template = "Bonjour {{prenom}}, je vois que vous êtes chez {{nom}}"
    # Data comes from Google Sheet with raw column names, normalized at storage time
    data = {"prenom": "Hugues", "nom": "123syndic", "site_web": "https://123syndic.com/"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, je vois que vous êtes chez 123syndic"


def test_render_template_unmatched_variable_left_as_is():
    template = "Bonjour {{prenom}}, votre code est {{code_promo}}"
    data = {"prenom": "Hugues"}
    result = render_template(template, data)
    assert result == "Bonjour Hugues, votre code est {{code_promo}}"


def test_render_template_no_variables():
    template = "Bonjour, ceci est un message sans variables."
    data = {"prenom": "Hugues"}
    result = render_template(template, data)
    assert result == "Bonjour, ceci est un message sans variables."


def test_render_template_empty_value():
    template = "Bonjour {{prenom}}"
    data = {"prenom": ""}
    result = render_template(template, data)
    assert result == "Bonjour "
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_variable_injection.py -v`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write implementation**

Create `app/services/__init__.py` (empty).

Create `app/services/variable_injection.py`:

```python
import re
import unicodedata


def normalize_column_name(name: str) -> str:
    """Normalize a Google Sheet column header to a variable name.

    Converts to lowercase, replaces spaces and slashes with underscores,
    removes accents, strips non-alphanumeric chars except underscores.
    """
    name = name.lower().strip()
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")
    name = re.sub(r"[/\s]+", "_", name)
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name)
    return name.strip("_")


def render_template(template: str, data: dict) -> str:
    """Replace {{variable}} placeholders with values from data.

    Unmatched variables are left as-is.
    """

    def replace_match(match):
        key = match.group(1).strip()
        if key in data:
            return str(data[key])
        return match.group(0)

    return re.sub(r"\{\{(\s*\w+\s*)\}\}", replace_match, template)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_variable_injection.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/__init__.py app/services/variable_injection.py tests/test_variable_injection.py
git commit -m "feat: variable injection service for template rendering"
```

---

### Task 4: Tracking Service

**Files:**
- Create: `app/services/tracking.py`
- Create: `tests/test_tracking.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_tracking.py`:

```python
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
        name="C1",
        template_id=template.id,
        status="in_progress",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db_session.add(campaign)
    db_session.commit()

    email = CampaignEmail(
        campaign_id=campaign.id,
        recipient_email="test@example.com",
        recipient_data={"prenom": "Jean"},
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="track-001",
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
        name="C1",
        template_id=template.id,
        status="in_progress",
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
        tracking_id="track-002",
        opened_at=datetime(2026, 6, 1, 11, 0),
    )
    db_session.add(email)
    db_session.commit()

    result = record_open(db_session, "track-002")
    assert result is not None
    assert result["first_open"] is False


def test_record_open_unknown_tracking_id(db_session):
    result = record_open(db_session, "nonexistent")
    assert result is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_tracking.py -v`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write implementation**

Create `app/services/tracking.py`:

```python
from datetime import datetime

from sqlalchemy.orm import Session

from app.models import CampaignEmail


def build_tracking_url(tracking_id: str, server_url: str) -> str:
    return f"{server_url}/penda/{tracking_id}"


def record_open(db: Session, tracking_id: str) -> dict | None:
    """Record an email open. Returns info dict or None if tracking_id not found.

    The dict includes a 'first_open' boolean to indicate whether this is the
    first time the email was opened (used to decide whether to send Telegram notification).
    """
    email = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.tracking_id == tracking_id)
        .first()
    )
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_tracking.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/tracking.py tests/test_tracking.py
git commit -m "feat: tracking service — record opens, build pixel URLs"
```

---

### Task 5: Telegram Notification Service

**Files:**
- Create: `app/services/telegram.py`
- Create: `tests/test_telegram.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_telegram.py`:

```python
from unittest.mock import AsyncMock, patch

import pytest

from app.services.telegram import format_open_notification, send_notification


def test_format_open_notification():
    data = {
        "recipient_email": "hugues@123syndic.com",
        "recipient_data": {
            "nom": "123syndic",
            "prenom": "Hugues",
            "nom_du_fondateur_decisionnaire": "Hugues Blondet",
            "telephone": "06 63 82 09 47",
        },
        "campaign_name": "Syndics Vague 1",
    }
    message = format_open_notification(data)
    assert "Email opened" in message or "ouvert" in message.lower() or "123syndic" in message
    assert "hugues@123syndic.com" in message
    assert "06 63 82 09 47" in message
    assert "Syndics Vague 1" in message


@pytest.mark.asyncio
async def test_send_notification_calls_telegram_api():
    with patch("app.services.telegram.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock()

        await send_notification("Hello test", bot_token="fake-token", chat_id="123")

        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "fake-token" in call_args[0][0]
        assert call_args[1]["json"]["chat_id"] == "123"
        assert call_args[1]["json"]["text"] == "Hello test"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_telegram.py -v`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write implementation**

Create `app/services/telegram.py`:

```python
from datetime import datetime

import httpx


def format_open_notification(data: dict) -> str:
    """Format a Telegram notification message for an email open event."""
    recipient_data = data.get("recipient_data", {})
    nom = recipient_data.get("nom", "—")
    prenom = recipient_data.get("prenom", "—")
    full_name = recipient_data.get("nom_du_fondateur_decisionnaire", "—")
    phone = recipient_data.get("telephone", "—")
    email = data.get("recipient_email", "—")
    campaign = data.get("campaign_name", "—")
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M")

    return (
        f"📬 Email ouvert\n"
        f"👤 {full_name} ({prenom})\n"
        f"🏢 {nom}\n"
        f"📧 {email}\n"
        f"📞 {phone}\n"
        f"📊 Campagne: {campaign}\n"
        f"🕐 {now}"
    )


async def send_notification(message: str, bot_token: str, chat_id: str) -> None:
    """Send a message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, json={"chat_id": chat_id, "text": message})
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_telegram.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/telegram.py tests/test_telegram.py
git commit -m "feat: Telegram notification service for email opens"
```

---

### Task 6: Google Sheets Service

**Files:**
- Create: `app/services/google_sheets.py`

This service depends on Google API credentials and cannot be unit-tested easily with a real sheet. We test it indirectly via route tests with mocking.

- [ ] **Step 1: Create app/services/google_sheets.py**

```python
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.config import settings
from app.services.variable_injection import normalize_column_name

import os
import json

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


def get_google_credentials() -> Credentials:
    """Load or refresh Google OAuth2 credentials."""
    creds = None
    token_path = settings.google_token_path

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.google_credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds


def fetch_prospects() -> list[dict]:
    """Fetch all rows from the Google Sheet and return as list of dicts
    with normalized column names.
    """
    creds = get_google_credentials()
    service = build("sheets", "v4", credentials=creds)
    sheet = service.spreadsheets()

    result = sheet.values().get(
        spreadsheetId=settings.google_sheet_id,
        range="A:Z",
    ).execute()

    values = result.get("values", [])
    if not values:
        return []

    raw_headers = values[0]
    headers = [normalize_column_name(h) for h in raw_headers]

    prospects = []
    for row in values[1:]:
        # Pad row to match header length
        padded_row = row + [""] * (len(headers) - len(row))
        prospect = dict(zip(headers, padded_row))
        prospects.append(prospect)

    return prospects
```

- [ ] **Step 2: Commit**

```bash
git add app/services/google_sheets.py
git commit -m "feat: Google Sheets service — fetch and normalize prospects"
```

---

### Task 7: Gmail Service

**Files:**
- Create: `app/services/gmail.py`

- [ ] **Step 1: Create app/services/gmail.py**

```python
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build

from app.services.google_sheets import get_google_credentials
from app.services.tracking import build_tracking_url
from app.config import settings


def _get_gmail_service():
    creds = get_google_credentials()
    return build("gmail", "v1", credentials=creds)


def send_email(
    to: str,
    subject: str,
    html_body: str,
    tracking_id: str,
    sender: str | None = None,
) -> str:
    """Send an email via Gmail API. Returns the Gmail message ID.

    Appends an invisible tracking pixel to the HTML body.
    """
    sender = sender or settings.gmail_sender_address
    tracking_url = build_tracking_url(tracking_id, settings.server_url)
    pixel = f'<img src="{tracking_url}" width="1" height="1" style="display:none" />'
    html_body_with_pixel = html_body + pixel

    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body_with_pixel, "html"))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service = _get_gmail_service()
    sent = service.users().messages().send(
        userId="me",
        body={"raw": raw},
    ).execute()

    return sent["id"]


def check_for_replies(gmail_message_ids: list[str]) -> dict[str, bool]:
    """Check which sent messages have received replies.

    Returns a dict of {gmail_message_id: has_reply}.
    """
    if not gmail_message_ids:
        return {}

    service = _get_gmail_service()
    results = {}

    for msg_id in gmail_message_ids:
        try:
            message = service.users().messages().get(
                userId="me", id=msg_id, format="metadata"
            ).execute()
            thread_id = message.get("threadId")

            thread = service.users().threads().get(
                userId="me", id=thread_id
            ).execute()

            # If thread has more than 1 message, there's a reply
            message_count = len(thread.get("messages", []))
            results[msg_id] = message_count > 1
        except Exception:
            results[msg_id] = False

    return results
```

- [ ] **Step 2: Commit**

```bash
git add app/services/gmail.py
git commit -m "feat: Gmail service — send emails with tracking pixel, detect replies"
```

---

### Task 8: Scheduler Service

**Files:**
- Create: `app/services/scheduler.py`
- Create: `tests/test_scheduler.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_scheduler.py`:

```python
import random
from datetime import datetime

from app.services.scheduler import generate_send_times


def test_generate_send_times_count():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    times = generate_send_times(5, start, end)
    assert len(times) == 5


def test_generate_send_times_within_range():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    random.seed(42)
    times = generate_send_times(10, start, end)
    for t in times:
        assert start <= t <= end


def test_generate_send_times_sorted():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 1, 18, 0)
    random.seed(42)
    times = generate_send_times(10, start, end)
    assert times == sorted(times)


def test_generate_send_times_multi_day():
    start = datetime(2026, 6, 1, 9, 0)
    end = datetime(2026, 6, 3, 18, 0)
    times = generate_send_times(20, start, end)
    assert len(times) == 20
    for t in times:
        assert start <= t <= end
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_scheduler.py -v`
Expected: FAIL — module does not exist.

- [ ] **Step 3: Write implementation**

Create `app/services/scheduler.py`:

```python
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

        # Check if all emails in campaign are done
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
            # Past due — send immediately
            send_single_email(email.id)
        else:
            schedule_campaign(db, email.campaign_id)
            break  # schedule_campaign handles all emails for a campaign


def init_scheduler() -> BackgroundScheduler:
    """Initialize and start the APScheduler."""
    global scheduler
    job_store = SQLAlchemyJobStore(url=settings.database_url)
    scheduler = BackgroundScheduler(jobstores={"default": job_store})
    scheduler.start()
    return scheduler


def shutdown_scheduler() -> None:
    """Shut down the scheduler."""
    global scheduler
    if scheduler:
        scheduler.shutdown()
        scheduler = None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_scheduler.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/services/scheduler.py tests/test_scheduler.py
git commit -m "feat: scheduler service — random send times, APScheduler integration"
```

---

### Task 9: Reply Checker Periodic Job

**Files:**
- Modify: `app/services/scheduler.py`

- [ ] **Step 1: Add reply checking to scheduler.py**

Append to `app/services/scheduler.py`:

```python
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
```

- [ ] **Step 2: Update init_scheduler to add the periodic reply check**

In `init_scheduler()`, after `scheduler.start()`, add:

```python
    scheduler.add_job(
        check_replies_job,
        "interval",
        minutes=5,
        id="check_replies",
        replace_existing=True,
    )
```

- [ ] **Step 3: Commit**

```bash
git add app/services/scheduler.py
git commit -m "feat: periodic reply detection via Gmail API"
```

---

### Task 10: FastAPI App & Base Template

**Files:**
- Create: `app/main.py`
- Create: `app/templates/base.html`
- Create: `static/style.css`
- Create: `app/routes/__init__.py`

- [ ] **Step 1: Create app/routes/__init__.py**

Empty file.

- [ ] **Step 2: Create static/style.css**

```css
:root {
    --bg: #f8f9fa;
    --card-bg: #ffffff;
    --primary: #2563eb;
    --primary-hover: #1d4ed8;
    --danger: #dc2626;
    --success: #16a34a;
    --warning: #d97706;
    --text: #1f2937;
    --text-light: #6b7280;
    --border: #e5e7eb;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
}

.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }

nav {
    background: var(--card-bg);
    border-bottom: 1px solid var(--border);
    padding: 1rem 0;
    margin-bottom: 2rem;
}

nav .container {
    display: flex;
    align-items: center;
    gap: 2rem;
}

nav a {
    color: var(--text);
    text-decoration: none;
    font-weight: 500;
}

nav a:hover { color: var(--primary); }
nav .logo { font-size: 1.25rem; font-weight: 700; }

h1, h2, h3 { margin-bottom: 1rem; }
h1 { font-size: 1.75rem; }

.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}

table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid var(--border); }
th { font-weight: 600; color: var(--text-light); font-size: 0.875rem; text-transform: uppercase; }
tr:hover { background: #f3f4f6; }
tr.clickable { cursor: pointer; }

.btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    font-weight: 500;
    text-decoration: none;
    border: none;
    cursor: pointer;
    font-size: 0.875rem;
}

.btn-primary { background: var(--primary); color: white; }
.btn-primary:hover { background: var(--primary-hover); }
.btn-danger { background: var(--danger); color: white; }
.btn-sm { padding: 0.25rem 0.5rem; font-size: 0.75rem; }

.badge {
    display: inline-block;
    padding: 0.125rem 0.5rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-draft { background: #e5e7eb; color: #374151; }
.badge-scheduled { background: #dbeafe; color: #1e40af; }
.badge-in_progress { background: #fef3c7; color: #92400e; }
.badge-completed { background: #d1fae5; color: #065f46; }
.badge-sent { background: #d1fae5; color: #065f46; }
.badge-pending { background: #dbeafe; color: #1e40af; }
.badge-failed { background: #fee2e2; color: #991b1b; }

.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 500; margin-bottom: 0.25rem; }
.form-group input, .form-group select, .form-group textarea {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid var(--border);
    border-radius: 6px;
    font-size: 0.875rem;
}
.form-group textarea { min-height: 200px; font-family: monospace; }

.alert {
    padding: 1rem;
    border-radius: 6px;
    margin-bottom: 1rem;
}
.alert-success { background: #d1fae5; color: #065f46; }
.alert-error { background: #fee2e2; color: #991b1b; }

.steps {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
}

.step {
    padding: 0.5rem 1rem;
    background: #e5e7eb;
    border-radius: 6px;
    font-size: 0.875rem;
    color: var(--text-light);
}

.step.active { background: var(--primary); color: white; }
.step.done { background: #d1fae5; color: #065f46; }

.stats { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat { text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: 700; }
.stat-label { font-size: 0.75rem; color: var(--text-light); }

.flex { display: flex; }
.justify-between { justify-content: space-between; }
.items-center { align-items: center; }
.gap-1 { gap: 0.5rem; }
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mb-2 { margin-bottom: 1rem; }

.checkbox-list { max-height: 400px; overflow-y: auto; }
.checkbox-list label { display: block; padding: 0.5rem; cursor: pointer; }
.checkbox-list label:hover { background: #f3f4f6; }
.checkbox-list input[type="checkbox"] { margin-right: 0.5rem; }

.preview-card { border: 1px solid var(--border); border-radius: 6px; padding: 1rem; margin-bottom: 1rem; }
.preview-card .preview-to { font-weight: 600; margin-bottom: 0.25rem; }
.preview-card .preview-subject { color: var(--text-light); margin-bottom: 0.5rem; }

.follow-up-item {
    padding: 0.75rem;
    border-left: 3px solid var(--primary);
    margin-bottom: 0.5rem;
    background: #f9fafb;
}
.follow-up-item .follow-up-date { font-size: 0.75rem; color: var(--text-light); }
```

- [ ] **Step 3: Create app/templates/base.html**

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}CRM{% endblock %}</title>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body>
    <nav>
        <div class="container">
            <a href="/" class="logo">CRM Prospection</a>
            <a href="/">Campagnes</a>
            <a href="/templates">Templates</a>
            <a href="/replies">Réponses</a>
            <a href="/admin/import">Import</a>
        </div>
    </nav>
    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

- [ ] **Step 4: Create app/main.py**

```python
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from app.database import Base, engine, SessionLocal
from app.services.scheduler import init_scheduler, shutdown_scheduler, reload_pending_jobs


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    init_scheduler()

    db = SessionLocal()
    try:
        reload_pending_jobs(db)
    finally:
        db.close()

    yield

    # Shutdown
    shutdown_scheduler()


app = FastAPI(lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key="crm-session-secret-key")

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Register routes
from app.routes.dashboard import router as dashboard_router
from app.routes.campaigns import router as campaigns_router
from app.routes.templates_routes import router as templates_router
from app.routes.replies import router as replies_router
from app.routes.admin import router as admin_router
from app.routes.penda import router as penda_router

app.include_router(dashboard_router)
app.include_router(campaigns_router)
app.include_router(templates_router)
app.include_router(replies_router)
app.include_router(admin_router)
app.include_router(penda_router)
```

- [ ] **Step 5: Commit**

```bash
git add app/main.py app/routes/__init__.py app/templates/base.html static/style.css
git commit -m "feat: FastAPI app with base HTML template, static CSS, lifespan"
```

---

### Task 11: Dashboard Route & Page

**Files:**
- Create: `app/routes/dashboard.py`
- Create: `app/templates/dashboard.html`
- Create: `tests/test_routes_dashboard.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_dashboard.py`:

```python
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine_test = create_engine("sqlite:///:memory:")
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_dashboard.py -v`
Expected: FAIL — routes do not exist yet.

- [ ] **Step 3: Create app/routes/dashboard.py**

```python
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Campaign, CampaignEmail
from app.main import templates

router = APIRouter()


@router.get("/")
def dashboard(request: Request, db: Session = Depends(get_db)):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()

    campaign_stats = []
    for c in campaigns:
        total = len(c.emails)
        sent = sum(1 for e in c.emails if e.send_status == "sent")
        opened = sum(1 for e in c.emails if e.opened_at is not None)
        replied = sum(1 for e in c.emails if e.reply_detected_at is not None)
        open_rate = round(opened / sent * 100, 1) if sent > 0 else 0
        reply_rate = round(replied / sent * 100, 1) if sent > 0 else 0

        campaign_stats.append({
            "campaign": c,
            "total": total,
            "sent": sent,
            "open_rate": open_rate,
            "reply_rate": reply_rate,
        })

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "campaign_stats": campaign_stats,
    })
```

- [ ] **Step 4: Create app/templates/dashboard.html**

```html
{% extends "base.html" %}
{% block title %}Dashboard — CRM{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-2">
    <h1>Campagnes</h1>
    <a href="/campaigns/new/step1" class="btn btn-primary">Nouvelle Campagne</a>
</div>

{% if campaign_stats %}
<div class="card">
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Template</th>
                <th>Période</th>
                <th>Statut</th>
                <th>Emails</th>
                <th>Taux d'ouverture</th>
                <th>Taux de réponse</th>
            </tr>
        </thead>
        <tbody>
            {% for item in campaign_stats %}
            <tr class="clickable" onclick="window.location='/campaigns/{{ item.campaign.id }}'">
                <td>{{ item.campaign.name }}</td>
                <td>{{ item.campaign.template.name }}</td>
                <td>
                    {% if item.campaign.send_start %}
                        {{ item.campaign.send_start.strftime('%d/%m/%Y %H:%M') }}
                        → {{ item.campaign.send_end.strftime('%d/%m/%Y %H:%M') }}
                    {% else %}
                        —
                    {% endif %}
                </td>
                <td><span class="badge badge-{{ item.campaign.status }}">{{ item.campaign.status }}</span></td>
                <td>{{ item.sent }} / {{ item.total }}</td>
                <td>{{ item.open_rate }}%</td>
                <td>{{ item.reply_rate }}%</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="card">
    <p>Aucune campagne pour le moment. <a href="/campaigns/new/step1">Créer votre première campagne</a></p>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Stub remaining route files so app can import**

Create minimal stubs for routes that `app/main.py` imports. Each file contains:

`app/routes/campaigns.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`app/routes/templates_routes.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`app/routes/replies.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`app/routes/admin.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

`app/routes/penda.py`:
```python
from fastapi import APIRouter
router = APIRouter()
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_routes_dashboard.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add app/routes/ app/templates/dashboard.html tests/test_routes_dashboard.py
git commit -m "feat: dashboard page with campaign stats"
```

---

### Task 12: Templates CRUD Routes & Pages

**Files:**
- Modify: `app/routes/templates_routes.py`
- Create: `app/templates/email_templates/list.html`
- Create: `app/templates/email_templates/create.html`
- Create: `app/templates/email_templates/edit.html`
- Create: `tests/test_routes_templates.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_templates.py`:

```python
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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


def test_templates_list_empty():
    response = client.get("/templates")
    assert response.status_code == 200
    assert "Templates" in response.text


def test_create_template():
    response = client.post("/templates/create", data={
        "name": "Welcome Template",
        "subject_template": "Bonjour {{prenom}}",
        "body_template": "<p>Hello {{prenom}} from {{nom}}</p>",
    }, follow_redirects=False)
    assert response.status_code == 303

    db = TestSession()
    template = db.query(Template).first()
    assert template is not None
    assert template.name == "Welcome Template"
    db.close()


def test_templates_list_with_data():
    db = TestSession()
    db.add(Template(name="T1", subject_template="S", body_template="B"))
    db.commit()
    db.close()

    response = client.get("/templates")
    assert response.status_code == 200
    assert "T1" in response.text


def test_edit_template():
    db = TestSession()
    t = Template(name="T1", subject_template="S", body_template="B")
    db.add(t)
    db.commit()
    tid = t.id
    db.close()

    response = client.get(f"/templates/{tid}/edit")
    assert response.status_code == 200
    assert "T1" in response.text

    response = client.post(f"/templates/{tid}/edit", data={
        "name": "T1 Updated",
        "subject_template": "New Subject",
        "body_template": "New Body",
    }, follow_redirects=False)
    assert response.status_code == 303

    db = TestSession()
    updated = db.query(Template).get(tid)
    assert updated.name == "T1 Updated"
    db.close()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_templates.py -v`
Expected: FAIL — routes not implemented.

- [ ] **Step 3: Implement app/routes/templates_routes.py**

```python
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template, CampaignEmail
from app.main import templates

router = APIRouter(prefix="/templates")


@router.get("")
def list_templates(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()

    template_stats = []
    for t in all_templates:
        campaign_count = len(t.campaigns)
        all_emails = []
        for c in t.campaigns:
            all_emails.extend(c.emails)

        sent = sum(1 for e in all_emails if e.send_status == "sent")
        opened = sum(1 for e in all_emails if e.opened_at is not None)
        replied = sum(1 for e in all_emails if e.reply_detected_at is not None)
        open_rate = round(opened / sent * 100, 1) if sent > 0 else 0
        reply_rate = round(replied / sent * 100, 1) if sent > 0 else 0

        template_stats.append({
            "template": t,
            "campaign_count": campaign_count,
            "sent": sent,
            "open_rate": open_rate,
            "reply_rate": reply_rate,
        })

    return templates.TemplateResponse("email_templates/list.html", {
        "request": request,
        "template_stats": template_stats,
    })


@router.get("/create")
def create_template_form(request: Request):
    return templates.TemplateResponse("email_templates/create.html", {
        "request": request,
    })


@router.post("/create")
def create_template(
    request: Request,
    name: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    db: Session = Depends(get_db),
):
    template = Template(
        name=name,
        subject_template=subject_template,
        body_template=body_template,
    )
    db.add(template)
    db.commit()
    return RedirectResponse(url="/templates", status_code=303)


@router.get("/{template_id}/edit")
def edit_template_form(template_id: int, request: Request, db: Session = Depends(get_db)):
    template = db.query(Template).get(template_id)
    return templates.TemplateResponse("email_templates/edit.html", {
        "request": request,
        "template": template,
    })


@router.post("/{template_id}/edit")
def edit_template(
    template_id: int,
    request: Request,
    name: str = Form(...),
    subject_template: str = Form(...),
    body_template: str = Form(...),
    db: Session = Depends(get_db),
):
    template = db.query(Template).get(template_id)
    template.name = name
    template.subject_template = subject_template
    template.body_template = body_template
    db.commit()
    return RedirectResponse(url="/templates", status_code=303)
```

- [ ] **Step 4: Create app/templates/email_templates/list.html**

```html
{% extends "base.html" %}
{% block title %}Templates — CRM{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-2">
    <h1>Templates</h1>
    <a href="/templates/create" class="btn btn-primary">Nouveau Template</a>
</div>

{% if template_stats %}
<div class="card">
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Campagnes</th>
                <th>Envoyés</th>
                <th>Taux d'ouverture</th>
                <th>Taux de réponse</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for item in template_stats %}
            <tr>
                <td>{{ item.template.name }}</td>
                <td>{{ item.campaign_count }}</td>
                <td>{{ item.sent }}</td>
                <td>{{ item.open_rate }}%</td>
                <td>{{ item.reply_rate }}%</td>
                <td><a href="/templates/{{ item.template.id }}/edit" class="btn btn-sm btn-primary">Modifier</a></td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="card">
    <p>Aucun template. <a href="/templates/create">Créer votre premier template</a></p>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Create app/templates/email_templates/create.html**

```html
{% extends "base.html" %}
{% block title %}Nouveau Template — CRM{% endblock %}

{% block content %}
<h1>Nouveau Template</h1>
<div class="card">
    <form method="post" action="/templates/create">
        <div class="form-group">
            <label>Nom du template</label>
            <input type="text" name="name" required>
        </div>
        <div class="form-group">
            <label>Objet (sujet de l'email)</label>
            <input type="text" name="subject_template" required placeholder="Bonjour {{prenom}}">
            <small style="color: var(--text-light)">Variables disponibles : {{nom}}, {{prenom}}, {{nom_du_fondateur_decisionnaire}}, {{email_du_decisionnaire}}, {{telephone}}, {{site_web}}, {{adresse}}</small>
        </div>
        <div class="form-group">
            <label>Corps du message (HTML)</label>
            <textarea name="body_template" required placeholder="<p>Bonjour {{prenom}},</p>"></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Créer</button>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 6: Create app/templates/email_templates/edit.html**

```html
{% extends "base.html" %}
{% block title %}Modifier Template — CRM{% endblock %}

{% block content %}
<h1>Modifier : {{ template.name }}</h1>
<div class="card">
    <form method="post" action="/templates/{{ template.id }}/edit">
        <div class="form-group">
            <label>Nom du template</label>
            <input type="text" name="name" value="{{ template.name }}" required>
        </div>
        <div class="form-group">
            <label>Objet (sujet de l'email)</label>
            <input type="text" name="subject_template" value="{{ template.subject_template }}" required>
            <small style="color: var(--text-light)">Variables disponibles : {{nom}}, {{prenom}}, {{nom_du_fondateur_decisionnaire}}, {{email_du_decisionnaire}}, {{telephone}}, {{site_web}}, {{adresse}}</small>
        </div>
        <div class="form-group">
            <label>Corps du message (HTML)</label>
            <textarea name="body_template" required>{{ template.body_template }}</textarea>
        </div>
        <button type="submit" class="btn btn-primary">Enregistrer</button>
        <a href="/templates" class="btn">Annuler</a>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `pytest tests/test_routes_templates.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 8: Commit**

```bash
git add app/routes/templates_routes.py app/templates/email_templates/ tests/test_routes_templates.py
git commit -m "feat: template CRUD pages with performance stats"
```

---

### Task 13: Campaign Wizard — Steps 1-5

**Files:**
- Modify: `app/routes/campaigns.py`
- Create: `app/templates/campaigns/wizard_step1.html`
- Create: `app/templates/campaigns/wizard_step2.html`
- Create: `app/templates/campaigns/wizard_step3.html`
- Create: `app/templates/campaigns/wizard_step4.html`
- Create: `app/templates/campaigns/wizard_step5.html`
- Create: `tests/test_routes_campaigns.py`

This is the largest task. The wizard stores progress in the server-side session between steps.

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_campaigns.py`:

```python
from datetime import datetime
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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
    db.close()

    # First go through step 1 to set session
    client.post("/campaigns/new/step1", data={
        "campaign_name": "Test",
        "template_id": str(t.id),
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
        name="C1",
        template_id=t.id,
        status="completed",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(c)
    db.commit()

    e = CampaignEmail(
        campaign_id=c.id,
        recipient_email="test@test.com",
        recipient_data={"prenom": "Test"},
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="t-100",
        sent_at=datetime(2026, 6, 1, 10, 5),
    )
    db.add(e)
    db.commit()
    cid = c.id
    db.close()

    response = client.get(f"/campaigns/{cid}")
    assert response.status_code == 200
    assert "test@test.com" in response.text
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_campaigns.py -v`
Expected: FAIL — routes not implemented.

- [ ] **Step 3: Implement app/routes/campaigns.py**

```python
import uuid
import json
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template, Campaign, CampaignEmail
from app.main import templates
from app.services.google_sheets import fetch_prospects
from app.services.variable_injection import render_template as render_vars
from app.services.scheduler import generate_send_times, schedule_campaign

router = APIRouter(prefix="/campaigns")


@router.get("/new/step1")
def wizard_step1(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse("campaigns/wizard_step1.html", {
        "request": request,
        "templates": all_templates,
    })


@router.post("/new/step1")
def wizard_step1_post(
    request: Request,
    campaign_name: str = Form(...),
    template_id: int = Form(...),
):
    request.session["wizard"] = {
        "campaign_name": campaign_name,
        "template_id": template_id,
    }
    return RedirectResponse(url="/campaigns/new/step2", status_code=303)


@router.get("/new/step2")
def wizard_step2(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    # Fetch prospects from Google Sheet
    prospects = fetch_prospects()

    # Filter out empty emails
    prospects = [p for p in prospects if p.get("email_du_decisionnaire", "").strip()]

    # Filter out already contacted emails
    existing_emails = {
        row[0] for row in db.query(CampaignEmail.recipient_email).all()
    }
    available = [p for p in prospects if p["email_du_decisionnaire"] not in existing_emails]

    return templates.TemplateResponse("campaigns/wizard_step2.html", {
        "request": request,
        "prospects": available,
        "wizard": wizard,
    })


@router.post("/new/step2")
def wizard_step2_post(
    request: Request,
    selected_emails: list[str] = Form(default=[]),
    auto_select_count: int = Form(default=0),
    db: Session = Depends(get_db),
):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    # Refetch to get full data for selected emails
    prospects = fetch_prospects()
    prospects = [p for p in prospects if p.get("email_du_decisionnaire", "").strip()]
    existing_emails = {
        row[0] for row in db.query(CampaignEmail.recipient_email).all()
    }
    available = [p for p in prospects if p["email_du_decisionnaire"] not in existing_emails]

    if auto_select_count > 0:
        selected = available[:auto_select_count]
    else:
        selected = [p for p in available if p["email_du_decisionnaire"] in selected_emails]

    wizard["recipients"] = selected
    request.session["wizard"] = wizard
    return RedirectResponse(url="/campaigns/new/step3", status_code=303)


@router.get("/new/step3")
def wizard_step3(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard or "recipients" not in wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    template = db.query(Template).get(wizard["template_id"])
    previews = []
    for recipient in wizard["recipients"]:
        previews.append({
            "email": recipient["email_du_decisionnaire"],
            "nom": recipient.get("nom", ""),
            "prenom": recipient.get("prenom", ""),
            "subject": render_vars(template.subject_template, recipient),
            "body": render_vars(template.body_template, recipient),
        })

    return templates.TemplateResponse("campaigns/wizard_step3.html", {
        "request": request,
        "previews": previews,
        "wizard": wizard,
    })


@router.post("/new/step3")
def wizard_step3_post(request: Request):
    return RedirectResponse(url="/campaigns/new/step4", status_code=303)


@router.get("/new/step4")
def wizard_step4(request: Request):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    return templates.TemplateResponse("campaigns/wizard_step4.html", {
        "request": request,
        "wizard": wizard,
    })


@router.post("/new/step4")
def wizard_step4_post(
    request: Request,
    send_start: str = Form(...),
    send_end: str = Form(...),
):
    wizard = request.session.get("wizard", {})
    wizard["send_start"] = send_start
    wizard["send_end"] = send_end
    request.session["wizard"] = wizard
    return RedirectResponse(url="/campaigns/new/step5", status_code=303)


@router.get("/new/step5")
def wizard_step5(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard or "send_start" not in wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    template = db.query(Template).get(wizard["template_id"])
    return templates.TemplateResponse("campaigns/wizard_step5.html", {
        "request": request,
        "wizard": wizard,
        "template": template,
    })


@router.post("/new/confirm")
def wizard_confirm(request: Request, db: Session = Depends(get_db)):
    wizard = request.session.get("wizard", {})
    if not wizard:
        return RedirectResponse(url="/campaigns/new/step1", status_code=303)

    send_start = datetime.fromisoformat(wizard["send_start"])
    send_end = datetime.fromisoformat(wizard["send_end"])

    campaign = Campaign(
        name=wizard["campaign_name"],
        template_id=wizard["template_id"],
        status="draft",
        send_start=send_start,
        send_end=send_end,
    )
    db.add(campaign)
    db.commit()

    template = db.query(Template).get(wizard["template_id"])
    recipients = wizard["recipients"]
    send_times = generate_send_times(len(recipients), send_start, send_end)

    for recipient, scheduled_at in zip(recipients, send_times):
        email = CampaignEmail(
            campaign_id=campaign.id,
            recipient_email=recipient["email_du_decisionnaire"],
            recipient_data=recipient,
            rendered_subject=render_vars(template.subject_template, recipient),
            rendered_body=render_vars(template.body_template, recipient),
            scheduled_at=scheduled_at,
            send_status="pending",
            tracking_id=str(uuid.uuid4()),
        )
        db.add(email)

    db.commit()

    schedule_campaign(db, campaign.id)

    # Clear wizard session
    request.session.pop("wizard", None)

    return RedirectResponse(url=f"/campaigns/{campaign.id}", status_code=303)


@router.get("/{campaign_id}")
def campaign_detail(campaign_id: int, request: Request, db: Session = Depends(get_db)):
    campaign = db.query(Campaign).get(campaign_id)
    emails = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.campaign_id == campaign_id)
        .order_by(CampaignEmail.scheduled_at)
        .all()
    )

    total = len(emails)
    sent = sum(1 for e in emails if e.send_status == "sent")
    opened = sum(1 for e in emails if e.opened_at is not None)
    replied = sum(1 for e in emails if e.reply_detected_at is not None)

    return templates.TemplateResponse("campaigns/detail.html", {
        "request": request,
        "campaign": campaign,
        "emails": emails,
        "total": total,
        "sent": sent,
        "opened": opened,
        "replied": replied,
    })
```

- [ ] **Step 4: Create app/templates/campaigns/wizard_step1.html**

```html
{% extends "base.html" %}
{% block title %}Nouvelle Campagne — Étape 1{% endblock %}

{% block content %}
<div class="steps">
    <span class="step active">1. Nom & Template</span>
    <span class="step">2. Destinataires</span>
    <span class="step">3. Aperçu</span>
    <span class="step">4. Planning</span>
    <span class="step">5. Confirmation</span>
</div>

<h1>Nouvelle Campagne</h1>
<div class="card">
    <form method="post" action="/campaigns/new/step1">
        <div class="form-group">
            <label>Nom de la campagne</label>
            <input type="text" name="campaign_name" required placeholder="Ex: Syndics Vague 2">
        </div>
        <div class="form-group">
            <label>Template</label>
            <select name="template_id" required>
                <option value="">— Choisir un template —</option>
                {% for t in templates %}
                <option value="{{ t.id }}">{{ t.name }}</option>
                {% endfor %}
            </select>
        </div>
        {% if not templates %}
        <p style="color: var(--danger)">Aucun template disponible. <a href="/templates/create">Créez-en un d'abord.</a></p>
        {% endif %}
        <button type="submit" class="btn btn-primary">Suivant →</button>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 5: Create app/templates/campaigns/wizard_step2.html**

```html
{% extends "base.html" %}
{% block title %}Nouvelle Campagne — Étape 2{% endblock %}

{% block content %}
<div class="steps">
    <span class="step done">1. Nom & Template</span>
    <span class="step active">2. Destinataires</span>
    <span class="step">3. Aperçu</span>
    <span class="step">4. Planning</span>
    <span class="step">5. Confirmation</span>
</div>

<h1>Sélection des destinataires</h1>
<div class="card">
    <p>{{ prospects|length }} adresses email disponibles (déjà contactés exclus)</p>

    <form method="post" action="/campaigns/new/step2">
        <div class="form-group">
            <label>Sélection automatique (nombre)</label>
            <input type="number" name="auto_select_count" min="0" max="{{ prospects|length }}" value="0"
                   placeholder="Ex: 10 pour sélectionner les 10 premiers">
            <small style="color: var(--text-light)">Mettez 0 pour sélectionner manuellement ci-dessous</small>
        </div>

        <div class="form-group">
            <label>Ou sélection manuelle :</label>
            <div class="checkbox-list">
                {% for p in prospects %}
                <label>
                    <input type="checkbox" name="selected_emails" value="{{ p.email_du_decisionnaire }}">
                    <strong>{{ p.get('nom', '') }}</strong> — {{ p.get('prenom', '') }}
                    ({{ p.email_du_decisionnaire }})
                </label>
                {% endfor %}
            </div>
        </div>

        <button type="submit" class="btn btn-primary">Suivant →</button>
        <a href="/campaigns/new/step1" class="btn">← Retour</a>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 6: Create app/templates/campaigns/wizard_step3.html**

```html
{% extends "base.html" %}
{% block title %}Nouvelle Campagne — Étape 3{% endblock %}

{% block content %}
<div class="steps">
    <span class="step done">1. Nom & Template</span>
    <span class="step done">2. Destinataires</span>
    <span class="step active">3. Aperçu</span>
    <span class="step">4. Planning</span>
    <span class="step">5. Confirmation</span>
</div>

<h1>Aperçu des emails ({{ previews|length }})</h1>
<form method="post" action="/campaigns/new/step3">
    {% for preview in previews %}
    <div class="preview-card">
        <div class="preview-to">À : {{ preview.email }} ({{ preview.prenom }} — {{ preview.nom }})</div>
        <div class="preview-subject">Objet : {{ preview.subject }}</div>
        <div>{{ preview.body | safe }}</div>
    </div>
    {% endfor %}

    <button type="submit" class="btn btn-primary">Suivant →</button>
    <a href="/campaigns/new/step2" class="btn">← Retour</a>
</form>
{% endblock %}
```

- [ ] **Step 7: Create app/templates/campaigns/wizard_step4.html**

```html
{% extends "base.html" %}
{% block title %}Nouvelle Campagne — Étape 4{% endblock %}

{% block content %}
<div class="steps">
    <span class="step done">1. Nom & Template</span>
    <span class="step done">2. Destinataires</span>
    <span class="step done">3. Aperçu</span>
    <span class="step active">4. Planning</span>
    <span class="step">5. Confirmation</span>
</div>

<h1>Planning d'envoi</h1>
<div class="card">
    <form method="post" action="/campaigns/new/step4">
        <div class="form-group">
            <label>Début de l'envoi</label>
            <input type="datetime-local" name="send_start" required>
        </div>
        <div class="form-group">
            <label>Fin de l'envoi</label>
            <input type="datetime-local" name="send_end" required>
        </div>
        <p style="color: var(--text-light); margin-bottom: 1rem;">
            Les emails seront envoyés à des horaires aléatoires dans cette plage.
        </p>
        <button type="submit" class="btn btn-primary">Suivant →</button>
        <a href="/campaigns/new/step3" class="btn">← Retour</a>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 8: Create app/templates/campaigns/wizard_step5.html**

```html
{% extends "base.html" %}
{% block title %}Nouvelle Campagne — Étape 5{% endblock %}

{% block content %}
<div class="steps">
    <span class="step done">1. Nom & Template</span>
    <span class="step done">2. Destinataires</span>
    <span class="step done">3. Aperçu</span>
    <span class="step done">4. Planning</span>
    <span class="step active">5. Confirmation</span>
</div>

<h1>Confirmation</h1>
<div class="card">
    <h2>Résumé</h2>
    <table>
        <tr><th>Campagne</th><td>{{ wizard.campaign_name }}</td></tr>
        <tr><th>Template</th><td>{{ template.name }}</td></tr>
        <tr><th>Destinataires</th><td>{{ wizard.recipients|length }} emails</td></tr>
        <tr><th>Début</th><td>{{ wizard.send_start }}</td></tr>
        <tr><th>Fin</th><td>{{ wizard.send_end }}</td></tr>
    </table>

    <form method="post" action="/campaigns/new/confirm" class="mt-2">
        <button type="submit" class="btn btn-primary">Lancer la Campagne</button>
        <a href="/campaigns/new/step4" class="btn">← Retour</a>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 9: Create app/templates/campaigns/detail.html**

```html
{% extends "base.html" %}
{% block title %}{{ campaign.name }} — CRM{% endblock %}

{% block content %}
<h1>{{ campaign.name }}</h1>

<div class="card">
    <div class="flex justify-between items-center">
        <div>
            <span class="badge badge-{{ campaign.status }}">{{ campaign.status }}</span>
            <span style="margin-left: 1rem; color: var(--text-light)">
                Template : {{ campaign.template.name }}
            </span>
        </div>
        <div style="color: var(--text-light)">
            {% if campaign.send_start %}
            {{ campaign.send_start.strftime('%d/%m/%Y %H:%M') }} → {{ campaign.send_end.strftime('%d/%m/%Y %H:%M') }}
            {% endif %}
        </div>
    </div>
</div>

<div class="stats">
    <div class="stat card">
        <div class="stat-value">{{ total }}</div>
        <div class="stat-label">Total</div>
    </div>
    <div class="stat card">
        <div class="stat-value">{{ sent }}</div>
        <div class="stat-label">Envoyés</div>
    </div>
    <div class="stat card">
        <div class="stat-value">{{ opened }}</div>
        <div class="stat-label">Ouverts</div>
    </div>
    <div class="stat card">
        <div class="stat-value">{{ replied }}</div>
        <div class="stat-label">Réponses</div>
    </div>
</div>

<div class="card">
    <table>
        <thead>
            <tr>
                <th>Destinataire</th>
                <th>Email</th>
                <th>Statut</th>
                <th>Planifié</th>
                <th>Envoyé</th>
                <th>Ouvert</th>
                <th>Réponse</th>
            </tr>
        </thead>
        <tbody>
            {% for email in emails %}
            <tr {% if email.send_status == 'failed' %}style="background: #fee2e2"{% endif %}>
                <td>{{ email.recipient_data.get('prenom', '') }} {{ email.recipient_data.get('nom', '') }}</td>
                <td>{{ email.recipient_email }}</td>
                <td><span class="badge badge-{{ email.send_status }}">{{ email.send_status }}</span></td>
                <td>{{ email.scheduled_at.strftime('%d/%m %H:%M') if email.scheduled_at else '—' }}</td>
                <td>{{ email.sent_at.strftime('%d/%m %H:%M') if email.sent_at else '—' }}</td>
                <td>{{ email.opened_at.strftime('%d/%m %H:%M') if email.opened_at else '—' }}</td>
                <td>{{ email.reply_detected_at.strftime('%d/%m %H:%M') if email.reply_detected_at else '—' }}</td>
            </tr>
            {% if email.send_status == 'failed' %}
            <tr style="background: #fee2e2">
                <td colspan="7" style="color: var(--danger); font-size: 0.875rem">
                    Erreur : {{ email.failure_reason }}
                </td>
            </tr>
            {% endif %}
            {% endfor %}
        </tbody>
    </table>
</div>

<a href="/" class="btn">← Retour aux campagnes</a>
{% endblock %}
```

- [ ] **Step 10: Run tests to verify they pass**

Run: `pytest tests/test_routes_campaigns.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 11: Commit**

```bash
git add app/routes/campaigns.py app/templates/campaigns/ tests/test_routes_campaigns.py
git commit -m "feat: campaign wizard (5 steps) + campaign detail page"
```

---

### Task 14: Tracking Pixel Endpoint (Penda)

**Files:**
- Modify: `app/routes/penda.py`
- Create: `tests/test_routes_penda.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_penda.py`:

```python
from datetime import datetime
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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


@patch("app.routes.penda.send_notification", new_callable=AsyncMock)
@patch("app.routes.penda.format_open_notification", return_value="test notification")
def test_penda_returns_pixel_and_records_open(mock_format, mock_send):
    db = TestSession()
    t = Template(name="T", subject_template="S", body_template="B")
    db.add(t)
    db.commit()

    c = Campaign(
        name="C1",
        template_id=t.id,
        status="in_progress",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(c)
    db.commit()

    e = CampaignEmail(
        campaign_id=c.id,
        recipient_email="test@test.com",
        recipient_data={"prenom": "Test", "nom": "Co"},
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="penda-001",
    )
    db.add(e)
    db.commit()
    db.close()

    response = client.get("/penda/penda-001")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/gif"

    # Verify open was recorded
    db2 = TestSession()
    updated = db2.query(CampaignEmail).filter_by(tracking_id="penda-001").first()
    assert updated.opened_at is not None
    db2.close()


def test_penda_unknown_tracking_id():
    response = client.get("/penda/nonexistent")
    assert response.status_code == 200  # Still returns pixel (don't leak info)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_penda.py -v`
Expected: FAIL — routes not implemented.

- [ ] **Step 3: Implement app/routes/penda.py**

```python
import base64

from fastapi import APIRouter, Depends, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.tracking import record_open
from app.services.telegram import format_open_notification, send_notification
from app.config import settings

router = APIRouter()

# 1x1 transparent GIF
PIXEL_GIF = base64.b64decode(
    "R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"
)


@router.get("/penda/{tracking_id}")
async def tracking_pixel(
    tracking_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    result = record_open(db, tracking_id)

    if result and result["first_open"]:
        message = format_open_notification(result)
        if settings.telegram_bot_token and settings.telegram_chat_id:
            background_tasks.add_task(
                send_notification,
                message,
                settings.telegram_bot_token,
                settings.telegram_chat_id,
            )

    return Response(
        content=PIXEL_GIF,
        media_type="image/gif",
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
        },
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_routes_penda.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/routes/penda.py tests/test_routes_penda.py
git commit -m "feat: tracking pixel endpoint /penda with Telegram notification"
```

---

### Task 15: Replies & Prospect Detail Routes

**Files:**
- Modify: `app/routes/replies.py`
- Create: `app/templates/replies/list.html`
- Create: `app/templates/replies/detail.html`
- Create: `tests/test_routes_replies.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_replies.py`:

```python
from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail, FollowUp

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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


def _create_replied_email(db):
    t = Template(name="T", subject_template="S", body_template="B")
    db.add(t)
    db.commit()

    c = Campaign(
        name="C1",
        template_id=t.id,
        status="completed",
        send_start=datetime(2026, 6, 1, 9, 0),
        send_end=datetime(2026, 6, 1, 18, 0),
    )
    db.add(c)
    db.commit()

    e = CampaignEmail(
        campaign_id=c.id,
        recipient_email="hugues@123syndic.com",
        recipient_data={
            "nom": "123syndic",
            "prenom": "Hugues",
            "nom_du_fondateur_decisionnaire": "Hugues Blondet",
            "telephone": "06 63 82 09 47",
            "email_du_decisionnaire": "hugues@123syndic.com",
        },
        rendered_subject="S",
        rendered_body="B",
        scheduled_at=datetime(2026, 6, 1, 10, 0),
        send_status="sent",
        tracking_id="r-001",
        sent_at=datetime(2026, 6, 1, 10, 5),
        reply_detected_at=datetime(2026, 6, 1, 14, 0),
    )
    db.add(e)
    db.commit()
    return e


def test_replies_list():
    db = TestSession()
    e = _create_replied_email(db)
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_replies.py -v`
Expected: FAIL — routes not implemented.

- [ ] **Step 3: Implement app/routes/replies.py**

```python
from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CampaignEmail, FollowUp
from app.main import templates

router = APIRouter(prefix="/replies")


@router.get("")
def replies_list(request: Request, db: Session = Depends(get_db)):
    replied_emails = (
        db.query(CampaignEmail)
        .filter(CampaignEmail.reply_detected_at.isnot(None))
        .order_by(CampaignEmail.reply_detected_at.desc())
        .all()
    )

    return templates.TemplateResponse("replies/list.html", {
        "request": request,
        "replied_emails": replied_emails,
    })


@router.get("/{campaign_email_id}")
def prospect_detail(campaign_email_id: int, request: Request, db: Session = Depends(get_db)):
    email = db.query(CampaignEmail).get(campaign_email_id)
    follow_ups = (
        db.query(FollowUp)
        .filter(FollowUp.campaign_email_id == campaign_email_id)
        .order_by(FollowUp.created_at.desc())
        .all()
    )

    return templates.TemplateResponse("replies/detail.html", {
        "request": request,
        "email": email,
        "follow_ups": follow_ups,
    })


@router.post("/{campaign_email_id}/follow-up")
def add_follow_up(
    campaign_email_id: int,
    note: str = Form(...),
    db: Session = Depends(get_db),
):
    follow_up = FollowUp(
        campaign_email_id=campaign_email_id,
        note=note,
    )
    db.add(follow_up)
    db.commit()
    return RedirectResponse(url=f"/replies/{campaign_email_id}", status_code=303)
```

- [ ] **Step 4: Create app/templates/replies/list.html**

```html
{% extends "base.html" %}
{% block title %}Réponses — CRM{% endblock %}

{% block content %}
<h1>Réponses</h1>

{% if replied_emails %}
<div class="card">
    <table>
        <thead>
            <tr>
                <th>Nom</th>
                <th>Entreprise</th>
                <th>Email</th>
                <th>Téléphone</th>
                <th>Campagne</th>
                <th>Date réponse</th>
            </tr>
        </thead>
        <tbody>
            {% for email in replied_emails %}
            <tr class="clickable" onclick="window.location='/replies/{{ email.id }}'">
                <td>{{ email.recipient_data.get('nom_du_fondateur_decisionnaire', email.recipient_data.get('prenom', '')) }}</td>
                <td>{{ email.recipient_data.get('nom', '') }}</td>
                <td>{{ email.recipient_email }}</td>
                <td>{{ email.recipient_data.get('telephone', '—') }}</td>
                <td>{{ email.campaign.name }}</td>
                <td>{{ email.reply_detected_at.strftime('%d/%m/%Y %H:%M') if email.reply_detected_at else '—' }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% else %}
<div class="card">
    <p>Aucune réponse reçue pour le moment.</p>
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 5: Create app/templates/replies/detail.html**

```html
{% extends "base.html" %}
{% block title %}{{ email.recipient_data.get('nom', '') }} — Détail{% endblock %}

{% block content %}
<h1>{{ email.recipient_data.get('nom_du_fondateur_decisionnaire', '') }}</h1>

<div class="card">
    <h2>Informations</h2>
    <table>
        <tr><th>Entreprise</th><td>{{ email.recipient_data.get('nom', '—') }}</td></tr>
        <tr><th>Nom complet</th><td>{{ email.recipient_data.get('nom_du_fondateur_decisionnaire', '—') }}</td></tr>
        <tr><th>Prénom</th><td>{{ email.recipient_data.get('prenom', '—') }}</td></tr>
        <tr><th>Email</th><td>{{ email.recipient_email }}</td></tr>
        <tr><th>Téléphone</th><td>{{ email.recipient_data.get('telephone', '—') }}</td></tr>
        <tr><th>Adresse</th><td>{{ email.recipient_data.get('adresse', '—') }}</td></tr>
        <tr><th>Site web</th><td>
            {% if email.recipient_data.get('site_web') %}
            <a href="{{ email.recipient_data.get('site_web') }}" target="_blank">{{ email.recipient_data.get('site_web') }}</a>
            {% else %}—{% endif %}
        </td></tr>
        <tr><th>LinkedIn</th><td>
            {% if email.recipient_data.get('linkedlin_du_fondateur_decisionnaire') %}
            <a href="{{ email.recipient_data.get('linkedlin_du_fondateur_decisionnaire') }}" target="_blank">Profil LinkedIn</a>
            {% else %}—{% endif %}
        </td></tr>
        <tr><th>Note Google</th><td>{{ email.recipient_data.get('note', '—') }}</td></tr>
        <tr><th>Horaires</th><td>{{ email.recipient_data.get('horaires', '—') }}</td></tr>
    </table>
</div>

<div class="card">
    <h2>Campagne</h2>
    <table>
        <tr><th>Campagne</th><td><a href="/campaigns/{{ email.campaign.id }}">{{ email.campaign.name }}</a></td></tr>
        <tr><th>Template</th><td>{{ email.campaign.template.name }}</td></tr>
        <tr><th>Envoyé le</th><td>{{ email.sent_at.strftime('%d/%m/%Y %H:%M') if email.sent_at else '—' }}</td></tr>
        <tr><th>Ouvert le</th><td>{{ email.opened_at.strftime('%d/%m/%Y %H:%M') if email.opened_at else '—' }}</td></tr>
        <tr><th>Réponse le</th><td>{{ email.reply_detected_at.strftime('%d/%m/%Y %H:%M') if email.reply_detected_at else '—' }}</td></tr>
    </table>
</div>

<div class="card">
    <div class="flex justify-between items-center mb-2">
        <h2>Suivi</h2>
    </div>

    <form method="post" action="/replies/{{ email.id }}/follow-up" class="mb-2">
        <div class="form-group">
            <textarea name="note" rows="2" required placeholder="Ex: Appelé, pas de réponse. Rappeler demain."></textarea>
        </div>
        <button type="submit" class="btn btn-primary">Ajouter une note</button>
    </form>

    {% if follow_ups %}
        {% for fu in follow_ups %}
        <div class="follow-up-item">
            <div class="follow-up-date">{{ fu.created_at.strftime('%d/%m/%Y %H:%M') if fu.created_at else '' }}</div>
            <div>{{ fu.note }}</div>
        </div>
        {% endfor %}
    {% else %}
        <p style="color: var(--text-light)">Aucune note de suivi.</p>
    {% endif %}
</div>

<a href="/replies" class="btn">← Retour aux réponses</a>
{% endblock %}
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `pytest tests/test_routes_replies.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add app/routes/replies.py app/templates/replies/ tests/test_routes_replies.py
git commit -m "feat: replies list + prospect detail page with follow-ups"
```

---

### Task 16: Admin Import Page

**Files:**
- Modify: `app/routes/admin.py`
- Create: `app/templates/admin/import.html`
- Create: `tests/test_routes_admin.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_routes_admin.py`:

```python
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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


def test_import_page():
    response = client.get("/admin/import")
    assert response.status_code == 200
    assert "Import" in response.text


def test_import_campaign():
    # First create a template
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_routes_admin.py -v`
Expected: FAIL — routes not implemented.

- [ ] **Step 3: Implement app/routes/admin.py**

```python
import uuid
from datetime import datetime

from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Template, Campaign, CampaignEmail
from app.main import templates

router = APIRouter(prefix="/admin")


@router.get("/import")
def import_page(request: Request, db: Session = Depends(get_db)):
    all_templates = db.query(Template).order_by(Template.created_at.desc()).all()
    return templates.TemplateResponse("admin/import.html", {
        "request": request,
        "templates": all_templates,
    })


@router.post("/import")
def import_campaign(
    request: Request,
    campaign_name: str = Form(...),
    template_id: int = Form(...),
    status: str = Form("completed"),
    emails: str = Form(...),
    send_status: str = Form("sent"),
    sent_date: str = Form(""),
    db: Session = Depends(get_db),
):
    sent_at = datetime.fromisoformat(sent_date) if sent_date else None

    campaign = Campaign(
        name=campaign_name,
        template_id=template_id,
        status=status,
        send_start=sent_at,
        send_end=sent_at,
    )
    db.add(campaign)
    db.commit()

    email_list = [e.strip() for e in emails.strip().split("\n") if e.strip()]

    for email_addr in email_list:
        ce = CampaignEmail(
            campaign_id=campaign.id,
            recipient_email=email_addr,
            recipient_data={},
            rendered_subject="(imported)",
            rendered_body="(imported)",
            scheduled_at=sent_at,
            sent_at=sent_at,
            send_status=send_status,
            tracking_id=str(uuid.uuid4()),
        )
        db.add(ce)

    db.commit()
    return RedirectResponse(url=f"/campaigns/{campaign.id}", status_code=303)
```

- [ ] **Step 4: Create app/templates/admin/import.html**

```html
{% extends "base.html" %}
{% block title %}Import Manuel — CRM{% endblock %}

{% block content %}
<h1>Import Manuel</h1>
<div class="card">
    <p style="color: var(--text-light); margin-bottom: 1rem;">
        Utilisez ce formulaire pour importer des campagnes déjà envoyées manuellement.
    </p>
    <form method="post" action="/admin/import">
        <div class="form-group">
            <label>Nom de la campagne</label>
            <input type="text" name="campaign_name" required placeholder="Ex: Campagne manuelle mai 2026">
        </div>
        <div class="form-group">
            <label>Template utilisé</label>
            <select name="template_id" required>
                <option value="">— Choisir —</option>
                {% for t in templates %}
                <option value="{{ t.id }}">{{ t.name }}</option>
                {% endfor %}
            </select>
            <small style="color: var(--text-light)">Créez d'abord le template si nécessaire</small>
        </div>
        <div class="form-group">
            <label>Statut de la campagne</label>
            <select name="status">
                <option value="completed">Terminée</option>
                <option value="in_progress">En cours</option>
            </select>
        </div>
        <div class="form-group">
            <label>Adresses email (une par ligne)</label>
            <textarea name="emails" required placeholder="email1@example.com
email2@example.com
email3@example.com"></textarea>
        </div>
        <div class="form-group">
            <label>Statut des emails</label>
            <select name="send_status">
                <option value="sent">Envoyé</option>
                <option value="failed">Échoué</option>
            </select>
        </div>
        <div class="form-group">
            <label>Date d'envoi</label>
            <input type="datetime-local" name="sent_date">
        </div>
        <button type="submit" class="btn btn-primary">Importer</button>
    </form>
</div>
{% endblock %}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_routes_admin.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/routes/admin.py app/templates/admin/ tests/test_routes_admin.py
git commit -m "feat: admin import page for manual campaign data entry"
```

---

### Task 17: Fix Circular Import (templates)

The `templates` Jinja2 object is created in `app/main.py` but imported by route files. This creates a circular import. Fix by extracting it.

**Files:**
- Create: `app/templating.py`
- Modify: `app/main.py`
- Modify: all route files

- [ ] **Step 1: Create app/templating.py**

```python
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="app/templates")
```

- [ ] **Step 2: Update app/main.py**

Remove the `templates = Jinja2Templates(...)` line from `main.py`. Remove the import of `Jinja2Templates`.

- [ ] **Step 3: Update all route files**

In each route file (`dashboard.py`, `campaigns.py`, `templates_routes.py`, `replies.py`, `admin.py`), change:

```python
from app.main import templates
```

to:

```python
from app.templating import templates
```

- [ ] **Step 4: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/templating.py app/main.py app/routes/
git commit -m "refactor: extract Jinja2 templates to avoid circular imports"
```

---

### Task 18: End-to-End Smoke Test

**Files:**
- Create: `tests/test_smoke.py`

- [ ] **Step 1: Write the smoke test**

Create `tests/test_smoke.py`:

```python
"""Smoke test: verify all pages load without errors."""

from datetime import datetime

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models import Template, Campaign, CampaignEmail, FollowUp

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine_test = create_engine("sqlite:///:memory:")
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
    db.close()
    return {"template_id": t.id, "campaign_id": c.id, "email_id": e.id}


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
```

- [ ] **Step 2: Run the smoke test**

Run: `pytest tests/test_smoke.py -v`
Expected: PASS.

- [ ] **Step 3: Run full test suite**

Run: `pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 4: Commit**

```bash
git add tests/test_smoke.py
git commit -m "test: smoke test for all pages"
```

---

### Task 19: Google OAuth2 Setup Documentation

**Files:**
- Create: `docs/google-api-setup.md`

- [ ] **Step 1: Write setup guide**

Create `docs/google-api-setup.md`:

```markdown
# Google API Setup

## 1. Create a Google Cloud Project

1. Go to https://console.cloud.google.com/
2. Create a new project (e.g., "CRM Prospection")

## 2. Enable APIs

In the project, go to "APIs & Services" > "Library" and enable:
- Google Sheets API
- Gmail API

## 3. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. Application type: "Desktop app"
4. Download the JSON file

## 4. Place Credentials

Save the downloaded file as `credentials/google_credentials.json` in the project root.

## 5. First Run (Generate Token)

On your first run, the app will open a browser window for OAuth2 consent.
After authorization, a `credentials/token.json` file will be created automatically.

For Docker deployment, you need to generate the token locally first:

```bash
# Run locally once to generate the token
python -c "from app.services.google_sheets import get_google_credentials; get_google_credentials()"
```

Then copy both files into the `credentials/` directory that's mounted in Docker.

## 6. Configure .env

```
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
GOOGLE_TOKEN_PATH=credentials/token.json
GOOGLE_SHEET_ID=<your-sheet-id>
GMAIL_SENDER_ADDRESS=your@gmail.com
```

The Sheet ID is the long string in the Google Sheet URL:
`https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit`
```

- [ ] **Step 2: Commit**

```bash
git add docs/google-api-setup.md
git commit -m "docs: Google API setup guide"
```

---

### Task 20: Telegram Bot Setup Documentation

**Files:**
- Modify: `docs/google-api-setup.md` (or create separate)

- [ ] **Step 1: Create docs/telegram-setup.md**

```markdown
# Telegram Bot Setup

## 1. Create a Bot

1. Open Telegram and search for `@BotFather`
2. Send `/newbot`
3. Follow the prompts to name your bot
4. Copy the **bot token** (looks like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

## 2. Get Your Chat ID

1. Send a message to your new bot
2. Open in browser: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
3. Find `"chat":{"id": <YOUR_CHAT_ID>}` in the response

## 3. Configure .env

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_CHAT_ID=987654321
```

## 4. Test

After starting the CRM, the bot will send you a notification when a prospect opens an email.
```

- [ ] **Step 2: Commit**

```bash
git add docs/telegram-setup.md
git commit -m "docs: Telegram bot setup guide"
```

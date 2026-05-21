# CRM Prospection Mail

A self-hosted CRM for managing cold email prospection campaigns. Built with FastAPI, Jinja2, and SQLite. Designed for personal use — simple, functional, no bloat.

## Features

- **Campaign management** — Create campaigns with a 5-step wizard: choose template, select recipients, preview emails, set schedule, send
- **Template engine** — Write email templates with `{{variables}}` (first name, company, etc.) auto-filled from your Google Sheet
- **Smart scheduling** — Emails are sent individually at random times within a configurable time window to avoid spam detection
- **Open tracking** — Invisible tracking pixel detects when a prospect opens your email
- **Telegram notifications** — Get a real-time Telegram message with prospect info when an email is opened, so you can call immediately
- **Reply detection** — Automatic Gmail thread monitoring to detect replies
- **Follow-up management** — Track your progress with each prospect who replied (called, meeting scheduled, etc.)
- **Google Sheets as source of truth** — Your prospect list lives in Google Sheets, the CRM fetches it via API
- **Admin import** — Import data from manually sent campaigns
- **Session-based auth** — Simple login page with username/password

## Screenshots

*Coming soon*

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | FastAPI (Python) |
| Frontend | Jinja2 templates + vanilla CSS |
| Database | SQLite |
| Scheduling | APScheduler |
| Email | Gmail API |
| Prospects | Google Sheets API |
| Notifications | Telegram Bot API |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Docker and Docker Compose
- A Google Cloud project with Sheets API and Gmail API enabled
- A Telegram bot (optional, for open notifications)

### 1. Clone and configure

```bash
git clone https://github.com/Decapix/crm-prospection-mail.git
cd crm-prospection-mail
cp .env.example .env
```

Edit `.env` with your values:

```
GOOGLE_SHEET_ID=your-sheet-id
GMAIL_SENDER_ADDRESS=your@gmail.com
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
SERVER_URL=http://localhost:8000
AUTH_USERNAME=admin
AUTH_PASSWORD=changeme
```

### 2. Set up Google API credentials

See [docs/google-api-setup.md](docs/google-api-setup.md) for detailed instructions.

```bash
mkdir -p credentials
# Place your google_credentials.json and token.json in credentials/
```

### 3. Run

```bash
docker compose up -d --build
```

Open `http://localhost:8000` and log in.

### 4. First steps

1. Go to **Templates** and create your first email template
2. Go to **Campagnes** and create a new campaign
3. Select recipients from your Google Sheet
4. Preview, schedule, and send

## Google Sheet Format

Your Google Sheet should have these columns (first row = headers):

| Column | Description |
|--------|-------------|
| nom | Company name |
| nom du fondateur/decisionnaire | Decision maker full name |
| prenom | First name |
| email du decisionnaire | Email address |
| telephone | Phone number |
| adresse | Address |
| site_web | Website |
| linkedlin du fondateur/decisionnaire | LinkedIn URL |
| note | Google rating |
| horaires | Business hours |
| google_maps_url | Google Maps link |

## Template Variables

Use `{{variable_name}}` in your templates. Available variables match your sheet columns:

```
{{nom}}, {{prenom}}, {{nom_du_fondateur_decisionnaire}},
{{email_du_decisionnaire}}, {{telephone}}, {{site_web}}, {{adresse}}
```

Example template body:
```
Bonjour {{prenom}},

Je me permets de vous contacter concernant {{nom}}...

Cordialement
```

## Deployment on a VM

See [docs/deployment.md](docs/deployment.md) for full deployment guide including:
- HTTPS with Caddy reverse proxy
- Timezone configuration
- Rsync-based deploys from your local machine

## Project Structure

```
app/
  main.py              # FastAPI app, middleware, lifespan
  config.py            # Settings from .env
  database.py          # SQLAlchemy setup
  models.py            # ORM models
  templating.py        # Jinja2 templates
  routes/
    dashboard.py       # Home page
    campaigns.py       # Campaign wizard + detail + edit
    templates_routes.py # Template CRUD
    replies.py         # Replies list + prospect detail
    admin.py           # Manual data import
    penda.py           # Tracking pixel endpoint
    auth.py            # Login/logout
  services/
    google_sheets.py   # Fetch prospects
    gmail.py           # Send emails, detect replies
    scheduler.py       # APScheduler jobs
    tracking.py        # Open tracking
    telegram.py        # Telegram notifications
```

## Docs

- [Google API Setup](docs/google-api-setup.md)
- [Telegram Bot Setup](docs/telegram-setup.md)
- [Deployment Guide](docs/deployment.md)

## License

MIT

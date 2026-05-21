# CRM Prospection — Design Spec

## Overview

A self-hosted CRM for managing email prospection campaigns targeting syndics (property management companies) in the Paris area. Built with FastAPI (API + server-rendered HTML via Jinja2) and SQLite. Deployed on a VM with Docker Compose.

**Source of truth for prospects:** A Google Sheet maintained manually, accessed via Google Sheets API.
**Email sending & reply detection:** Gmail API.
**Notifications:** Telegram bot for real-time open alerts.

Security and advanced features are not priorities — the goal is a functional personal tool.

## Tech Stack

- **Backend:** FastAPI (API + HTML rendering)
- **Frontend:** Jinja2 templates + simple CSS (Tailwind CDN or Pico CSS, no build step)
- **Database:** SQLite via SQLAlchemy ORM
- **Scheduling:** APScheduler (in-process, jobs persisted to SQLite)
- **Google APIs:** `google-api-python-client` for Sheets + Gmail
- **Notifications:** Telegram Bot API (direct HTTP POST)
- **Deployment:** Docker Compose (single container + SQLite volume)

## Database Schema

### `templates`

| Column           | Type        | Description                           |
|------------------|-------------|---------------------------------------|
| id               | INTEGER PK  | Auto-increment                        |
| name             | TEXT        | Template name                         |
| subject_template | TEXT        | Subject with `{{variables}}`          |
| body_template    | TEXT        | Body (HTML) with `{{variables}}`      |
| created_at       | DATETIME    |                                       |

### `campaigns`

| Column      | Type              | Description                                    |
|-------------|-------------------|------------------------------------------------|
| id          | INTEGER PK        | Auto-increment                                 |
| name        | TEXT              | Campaign name                                  |
| template_id | FK → templates    |                                                |
| status      | TEXT              | `draft`, `scheduled`, `in_progress`, `completed` |
| send_start  | DATETIME          | Start of sending window                        |
| send_end    | DATETIME          | End of sending window                          |
| created_at  | DATETIME          |                                                |

### `campaign_emails`

| Column           | Type                  | Description                              |
|------------------|-----------------------|------------------------------------------|
| id               | INTEGER PK            |                                          |
| campaign_id      | FK → campaigns        |                                          |
| recipient_email  | TEXT                  |                                          |
| recipient_data   | JSON                  | Full row from Google Sheet               |
| rendered_subject | TEXT                  | Subject after variable substitution      |
| rendered_body    | TEXT                  | Body after variable substitution         |
| scheduled_at     | DATETIME              | Random time within campaign window       |
| sent_at          | DATETIME              | NULL until sent                          |
| send_status      | TEXT                  | `pending`, `sent`, `failed`              |
| failure_reason   | TEXT                  | NULL or error message                    |
| tracking_id      | TEXT UNIQUE           | UUID for tracking pixel                  |
| gmail_message_id | TEXT                  | Gmail message ID (for reply detection)   |
| opened_at        | DATETIME              | NULL until first open                    |
| reply_detected_at| DATETIME              | NULL until reply found                   |

### `follow_ups`

| Column           | Type                    | Description            |
|------------------|-------------------------|------------------------|
| id               | INTEGER PK              |                        |
| campaign_email_id| FK → campaign_emails    |                        |
| note             | TEXT                    | Free-form text         |
| created_at       | DATETIME                |                        |

## Project Structure

```
crm/
├── app/
│   ├── main.py                  # FastAPI app, startup (APScheduler)
│   ├── config.py                # Settings (Gmail, Google Sheets, Telegram, etc.)
│   ├── database.py              # SQLite connection, SQLAlchemy setup
│   ├── models.py                # SQLAlchemy models
│   ├── services/
│   │   ├── google_sheets.py     # Fetch prospects from Google Sheet
│   │   ├── gmail.py             # Send emails, check replies via Gmail API
│   │   ├── scheduler.py         # APScheduler: schedule & send campaign emails
│   │   ├── tracking.py          # Tracking pixel logic + open logging
│   │   └── telegram.py          # Telegram bot notifications
│   ├── routes/
│   │   ├── dashboard.py         # Home page: campaign summary
│   │   ├── campaigns.py         # Campaign wizard + detail pages
│   │   ├── templates_routes.py  # Template CRUD + performance stats
│   │   ├── replies.py           # Replies list + prospect detail + follow-ups
│   │   ├── admin.py             # Admin: manual import of campaigns/emails
│   │   └── penda.py             # Tracking pixel endpoint
│   └── templates/               # Jinja2 HTML templates
│       ├── base.html
│       ├── dashboard.html
│       ├── campaigns/
│       │   ├── list.html
│       │   ├── detail.html
│       │   ├── wizard_step1.html  # Name + template selection
│       │   ├── wizard_step2.html  # Recipient selection
│       │   ├── wizard_step3.html  # Preview rendered emails
│       │   ├── wizard_step4.html  # Schedule (start/end datetime)
│       │   └── wizard_step5.html  # Confirm & send
│       ├── templates/
│       │   ├── list.html
│       │   ├── create.html
│       │   └── edit.html
│       ├── replies/
│       │   ├── list.html
│       │   └── detail.html
│       └── admin/
│           └── import.html
├── static/                      # CSS
├── crm.db                       # SQLite (volume-mounted in Docker)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                         # Google API creds, Telegram config, sender email
```

## Pages & User Flows

### Page 1 — Dashboard (Home: `/`)

- Table of all campaigns, sorted by most recent first
- Each row: campaign name, template used, date range, status, email count, open rate, reply rate
- Click a campaign row → campaign detail page
- "Create Campaign" button → campaign wizard

### Page 2 — Campaign Detail (`/campaigns/{id}`)

- Campaign info header: name, template, schedule, status
- Table of all emails in the campaign:
  - Recipient name, email, send status, scheduled/sent time, opened (yes/no + time), replied (yes/no + time)
  - Failed emails highlighted with error reason

### Page 3 — Campaign Creation Wizard (`/campaigns/new`)

Multi-step form:

1. **Step 1 — Name + Template** (`/campaigns/new/step1`): Enter campaign name, select existing template from dropdown
2. **Step 2 — Recipients** (`/campaigns/new/step2`): FastAPI fetches emails from Google Sheet, removes already-contacted emails, removes rows with empty email. User either manually checks emails or enters a number N to auto-select the first N
3. **Step 3 — Preview** (`/campaigns/new/step3`): Shows all emails rendered with variables filled in (subject + body per recipient)
4. **Step 4 — Schedule** (`/campaigns/new/step4`): Form with start datetime and end datetime
5. **Step 5 — Confirm** (`/campaigns/new/step5`): Summary of everything. Click "Send Campaign" to schedule

### Page 4 — Templates (`/templates`)

- List of all templates
- Each row: template name, number of campaigns using it, total emails sent, open rate, reply rate
- Click → view/edit template
- "Create Template" button → form with name, subject template, body template
- Variable hints displayed (available columns from Google Sheet)

### Page 5 — Replies (`/replies`)

- One row per campaign_email that has `reply_detected_at` set
- Shows: prospect name, company name, email, phone, campaign name, reply date
- Click row → prospect detail page

### Page 6 — Prospect Detail (`/replies/{campaign_email_id}`)

- All company info from Google Sheet (all columns from `recipient_data`)
- Campaign and template info
- Follow-up section: list of free-form notes with timestamps
- "Add follow-up" form to add new entries

### Page 7 — Admin Import (`/admin/import`)

- Form to manually create a campaign with a template and insert sent emails
- Used to import the 10 emails from the existing manual campaign
- Fields: campaign name, template selection, then a table/form to add emails with: recipient email, recipient data, sent date, send status, open/reply status

## Technical Behaviors

### Email Sending

- When a campaign is confirmed, FastAPI generates a random `scheduled_at` time for each email within `[send_start, send_end]`
- APScheduler creates one job per email at its `scheduled_at` time
- On startup, FastAPI reloads all `pending` campaign emails from SQLite and reschedules them
- Each email sent individually via Gmail API (not batch)
- Sender address configured in `.env`, abstracted behind a sender service for future multi-address support
- Gmail message ID stored in `campaign_emails.gmail_message_id` for reply tracking

### Tracking Pixel

- Each email gets a unique `tracking_id` (UUID)
- An invisible `<img src="https://{server}/penda/{tracking_id}">` is appended to the email body
- Endpoint `GET /penda/{tracking_id}` returns a 1x1 transparent GIF and logs `opened_at`
- First open: updates DB + sends Telegram notification
- Subsequent opens: updates `opened_at` timestamp, no repeated Telegram notification

### Telegram Notifications

- On first email open, sends a message to the configured Telegram chat with:
  - Prospect name, company, email, phone
  - Campaign name
  - Open timestamp
- Configuration: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in `.env`
- Simple HTTP POST to `https://api.telegram.org/bot{token}/sendMessage`

### Reply Detection

- APScheduler periodic job (every 5 minutes) checks Gmail API for replies
- Matches replies using `gmail_message_id` (thread ID / `In-Reply-To` header)
- Updates `reply_detected_at` in the database when a reply is found

### Variable Injection

- Templates use `{{variable_name}}` syntax
- Variable names map to Google Sheet column headers (normalized: spaces → underscores, lowercase)
- Column mapping: `nom` → `{{nom}}`, `prenom` → `{{prenom}}`, `nom_du_fondateur_decisionnaire` → `{{nom_du_fondateur_decisionnaire}}`, etc.
- At preview and send time, `recipient_data` JSON is used to substitute all variables
- Unmatched variables left as-is (visible in preview so user can fix)

### Recipient Filtering

- Fetch all rows from Google Sheet via Sheets API
- Exclude rows with empty `email du decisionnaire` column
- Exclude emails already present in `campaign_emails` table (any previous campaign, any status)
- Return filtered list for selection in wizard step 2

## Deployment

### Docker Compose

```yaml
services:
  crm:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - crm_data:/app/data    # SQLite database
    env_file:
      - .env

volumes:
  crm_data:
```

### Environment Variables (`.env`)

```
# Google API
GOOGLE_CREDENTIALS_PATH=/app/credentials/google_credentials.json
GOOGLE_SHEET_ID=<sheet-id>

# Gmail
GMAIL_SENDER_ADDRESS=your@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=<bot-token>
TELEGRAM_CHAT_ID=<chat-id>

# Server
SERVER_URL=https://your-domain.com   # For tracking pixel URLs
```

### Google API Setup

User must:
1. Create a Google Cloud project
2. Enable Google Sheets API and Gmail API
3. Create OAuth2 credentials (or service account for Sheets)
4. Download the credentials JSON file
5. Mount it in the Docker container

## Google Sheet Columns Reference

| Column Header | Variable Name | Example |
|---|---|---|
| nom | `{{nom}}` | 123syndic |
| nom du fondateur/decisionnaire | `{{nom_du_fondateur_decisionnaire}}` | Hugues Blondet |
| prenom | `{{prenom}}` | Hugues |
| linkedlin du fondateur/decisionnaire | `{{linkedlin_du_fondateur_decisionnaire}}` | https://linkedin.com/in/... |
| email du decisionnaire | `{{email_du_decisionnaire}}` | hugues.blondet@123syndic.com |
| adresse | `{{adresse}}` | 5bis Villa Emile Bergerat... |
| telephone | `{{telephone}}` | 06 63 82 09 47 |
| site_web | `{{site_web}}` | https://123syndic.com/ |
| note | `{{note}}` | 5 |
| horaires | `{{horaires}}` | lundi: 08:00 – 21:00 ... |
| google_maps_url | `{{google_maps_url}}` | https://maps.google.com/... |

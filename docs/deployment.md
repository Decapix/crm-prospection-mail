# Deployment Guide — CRM Prospection

## Prerequisites

- A VM with Docker and Docker Compose installed
- A domain name (or public IP) pointing to your VM
- Google Cloud credentials (see `docs/google-api-setup.md`)
- Telegram bot (see `docs/telegram-setup.md`)

## 1. Clone the project on your VM

```bash
ssh your-vm
git clone <your-repo-url> crm
cd crm
```

## 2. Generate Google OAuth token (local machine)

The OAuth flow needs a browser, so do this on your local machine first:

```bash
pip install google-api-python-client google-auth-oauthlib
python3 -c "
from app.services.google_sheets import get_google_credentials
get_google_credentials()
"
```

This opens a browser for consent. After authorizing, it creates `credentials/token.json`.

Then copy both files to your VM:

```bash
scp credentials/google_credentials.json your-vm:~/crm/credentials/
scp credentials/token.json your-vm:~/crm/credentials/
```

## 3. Configure .env

On the VM:

```bash
cp .env.example .env
nano .env
```

Fill in all values:

```
# Google API
GOOGLE_CREDENTIALS_PATH=credentials/google_credentials.json
GOOGLE_TOKEN_PATH=credentials/token.json
GOOGLE_SHEET_ID=<the long ID from your Google Sheet URL>

# Gmail
GMAIL_SENDER_ADDRESS=your@gmail.com

# Telegram
TELEGRAM_BOT_TOKEN=<from BotFather>
TELEGRAM_CHAT_ID=<your chat ID>

# Server — IMPORTANT: must be your public URL for tracking pixels to work
SERVER_URL=http://YOUR_VM_IP:8000

# Database
DATABASE_URL=sqlite:///./data/crm.db

# Auth
AUTH_USERNAME=<choose a username>
AUTH_PASSWORD=<choose a strong password>
```

**Important:** `SERVER_URL` must be reachable from the internet for the tracking pixel to work. If you use a domain with HTTPS (recommended), set it to `https://crm.yourdomain.com`.

## 4. Set timezone (optional)

The container uses UTC by default. To use Paris time, add this to `docker-compose.yml` under the `crm` service:

```yaml
    environment:
      - TZ=Europe/Paris
```

## 5. Build and start

```bash
docker compose up -d --build
```

Check logs:

```bash
docker compose logs -f
```

The CRM is now accessible at `http://YOUR_VM_IP:8000`.

## 6. Verify

1. Open `http://YOUR_VM_IP:8000` — you should see the login page
2. Log in with your `AUTH_USERNAME` / `AUTH_PASSWORD`
3. Go to Templates → create your first template
4. Go to Admin Import → import your existing 10 emails
5. Create a new campaign to test the full flow

## 7. Reverse proxy with HTTPS (recommended)

For HTTPS (needed for tracking pixels to work reliably in email clients), use Caddy or Nginx as a reverse proxy.

### With Caddy (easiest)

Add to `docker-compose.yml`:

```yaml
  caddy:
    image: caddy:2
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile
      - caddy_data:/data
    restart: unless-stopped
```

Add `caddy_data:` to the `volumes:` section.

Create `Caddyfile`:

```
crm.yourdomain.com {
    reverse_proxy crm:8000
}
```

Then change the CRM port in `docker-compose.yml` from `"8000:8000"` to `expose: ["8000"]` (internal only).

Update `.env`:

```
SERVER_URL=https://crm.yourdomain.com
```

## 8. Updating

```bash
cd crm
git pull
docker compose up -d --build
```

Data is persisted in the `crm_data` Docker volume — it survives rebuilds.

## Troubleshooting

### Tracking pixel not working
- Check `SERVER_URL` in `.env` — it must be publicly accessible
- Gmail proxies images through Google servers, so your server must be reachable from the internet
- Check logs: `docker compose logs -f` — you should see `GET /penda/...` requests when emails are opened

### Google API errors
- Make sure Google Sheets API and Gmail API are enabled in your Google Cloud project
- If token expires, regenerate it locally and copy `token.json` to the VM

### Emails not sending
- Check logs for APScheduler errors
- Verify Gmail API is enabled and credentials are valid
- Check that the scheduled send time hasn't already passed

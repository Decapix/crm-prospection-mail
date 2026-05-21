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

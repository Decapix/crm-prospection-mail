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
        padded_row = row + [""] * (len(headers) - len(row))
        prospect = dict(zip(headers, padded_row))
        prospects.append(prospect)

    return prospects

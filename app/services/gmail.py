import base64
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from googleapiclient.discovery import build

from app.services.google_sheets import get_google_credentials
from app.services.tracking import build_tracking_url
from app.config import settings

logger = logging.getLogger(__name__)


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

            message_count = len(thread.get("messages", []))
            has_reply = message_count > 1
            results[msg_id] = has_reply
            logger.info(f"Reply check for {msg_id}: thread={thread_id}, messages={message_count}, has_reply={has_reply}")
        except Exception as e:
            logger.error(f"Reply check failed for {msg_id}: {e}")
            results[msg_id] = False

    return results

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

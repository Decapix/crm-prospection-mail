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
    assert "123syndic" in message
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

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

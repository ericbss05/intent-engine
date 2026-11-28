import json
import logging
import time

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import ApiError
from app.core.webhook import verify_signature
from app.services import user_data

logger = logging.getLogger("app.webhook")
router = APIRouter(prefix="/webhooks", tags=["webhooks"])

_MAX_BODY_BYTES = 64 * 1024


class _EventData(BaseModel):
    id: str


class _ClerkEvent(BaseModel):
    type: str
    data: _EventData


@router.post("/clerk")
async def clerk_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    secret = getattr(request.app.state, "clerk_webhook_secret", None)
    if secret is None:
        raise ApiError(503, "webhook_unavailable", "Webhook is not configured")

    body = await request.body()
    if len(body) > _MAX_BODY_BYTES:
        raise ApiError(413, "payload_too_large", "Payload too large")

    # La signature est vérifiée sur le corps BRUT, avant tout traitement du contenu.
    ok = verify_signature(
        secret=secret,
        msg_id=request.headers.get("svix-id", ""),
        timestamp=request.headers.get("svix-timestamp", ""),
        signature_header=request.headers.get("svix-signature", ""),
        body=body,
        now_epoch=time.time(),
    )
    if not ok:
        raise ApiError(400, "invalid_signature", "Invalid webhook signature")

    try:
        event = _ClerkEvent.model_validate(json.loads(body))
    except (ValueError, ValidationError) as exc:
        raise ApiError(400, "invalid_payload", "Invalid webhook payload") from exc

    # Le corps contient des emails et des noms : on ne le logge jamais, seulement le type.
    if event.type == "user.created":
        user_data.ensure_profile(db, event.data.id)
    elif event.type == "user.deleted":
        user_data.delete_user_data(db, event.data.id)
    logger.info("clerk_webhook", extra={"event": event.type})
    return {"status": "ok"}

"""Garde « consentement IA » (R12) : sans accord explicite, AUCUN appel à une IA.

Toute fonction qui enverrait des données à un LLM (parties 4, 5 et 10) doit d'abord appeler
`require_ai_consent(db, user_id)`. Le journal `consents` fait foi (dernier état connu) ;
un retrait prend effet immédiatement.
"""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import ApiError
from app.core.security import CurrentUser
from app.routers.deps import require_adult
from app.services.consents import latest_consent


def has_ai_consent(db: Session, user_id: str) -> bool:
    row = latest_consent(db, user_id, "ai_assist")
    return bool(row and row.granted)


def require_ai_consent(db: Session, user_id: str) -> None:
    if not has_ai_consent(db, user_id):
        raise ApiError(403, "ai_consent_required", "AI-assisted analysis was not accepted")


def ai_consent_required(
    user: CurrentUser = Depends(require_adult), db: Session = Depends(get_db)
) -> CurrentUser:
    """Dépendance FastAPI pour les futures routes qui déclenchent une analyse par IA."""
    require_ai_consent(db, user.user_id)
    return user

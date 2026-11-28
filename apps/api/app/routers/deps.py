from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import ApiError
from app.core.security import CurrentUser, get_current_user
from app.interfaces.identity import IdentityProvider
from app.services import user_data


def require_adult(
    user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> CurrentUser:
    """Bloque les fonctions du service tant que « 18 ans ou plus » n'est pas confirmé (R13).

    À utiliser sur toutes les routes métier des parties suivantes. Les droits (export,
    suppression) n'en dépendent pas : on ne retient jamais quelqu'un de supprimer ses données.
    """
    if not user_data.is_adult_confirmed(db, user.user_id):
        raise ApiError(403, "adult_confirmation_required", "Age confirmation required")
    return user


def get_identity_provider(request: Request) -> IdentityProvider:
    provider: IdentityProvider | None = getattr(request.app.state, "identity_provider", None)
    if provider is None:
        raise ApiError(503, "identity_unavailable", "Identity provider is not configured")
    return provider

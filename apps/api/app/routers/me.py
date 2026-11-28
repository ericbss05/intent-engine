import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import ApiError
from app.core.security import CurrentUser, get_current_user
from app.interfaces.identity import IdentityError, IdentityProvider
from app.routers.deps import get_identity_provider
from app.services import user_data

logger = logging.getLogger("app.me")
router = APIRouter(prefix="/me", tags=["me"])


class MeResponse(BaseModel):
    adult_confirmed: bool
    ai_assist_consent: bool
    created_at: datetime
    is_admin: bool


class AdultConfirmationRequest(BaseModel):
    # Seule la valeur True est acceptée : un refus n'est pas enregistré (R13).
    confirmed: Literal[True]


@router.get("", response_model=MeResponse)
def get_me(
    user: CurrentUser = Depends(get_current_user), db: Session = Depends(get_db)
) -> MeResponse:
    profile = user_data.get_profile(db, user.user_id)
    if profile is None:
        raise ApiError(404, "profile_not_found", "Profile not found")
    user_data.touch_last_active(db, user.user_id)
    return MeResponse(
        adult_confirmed=profile.adult_confirmed_at is not None,
        ai_assist_consent=profile.ai_assist_consent,
        created_at=profile.created_at,
        is_admin=user.is_admin,
    )


@router.post("/adult-confirmation", response_model=MeResponse)
def confirm_adult(
    body: AdultConfirmationRequest,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> MeResponse:
    # Crée aussi le profil si le webhook Clerk n'est pas encore arrivé.
    profile = user_data.confirm_adult(db, user.user_id)
    return MeResponse(
        adult_confirmed=True,
        ai_assist_consent=profile.ai_assist_consent,
        created_at=profile.created_at,
        is_admin=user.is_admin,
    )


@router.get("/export")
def export_me(
    response: Response,
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    response.headers["Cache-Control"] = "no-store"  # contient des données personnelles
    response.headers["Content-Disposition"] = 'attachment; filename="mes-donnees.json"'
    return user_data.export_user_data(db, user.user_id)


@router.delete("", status_code=204)
def delete_me(
    user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    identity: IdentityProvider = Depends(get_identity_provider),
) -> Response:
    # 1) Nos données d'abord, et on valide AVANT d'appeler Clerk : si Clerk est en panne,
    #    les données sont déjà effacées (priorité RGPD) et l'étudiant peut simplement réessayer.
    user_data.delete_user_data(db, user.user_id)
    db.commit()
    # 2) Le compte chez Clerk.
    try:
        identity.delete_user(user.user_id)
    except IdentityError as exc:
        logger.error("identity_deletion_failed", extra={"event": "identity_deletion_failed"})
        raise ApiError(
            502,
            "identity_deletion_failed",
            "Your data was deleted but the account removal must be retried",
        ) from exc
    return Response(status_code=204)

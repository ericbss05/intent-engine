from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.errors import ApiError
from app.core.security import CurrentUser
from app.domain.models import SearchPreferences
from app.domain.reference import ReferenceData
from app.domain.schemas import PreferencesIn, PreferencesOut
from app.routers.deps import require_adult
from app.services import preferences as service

router = APIRouter(prefix="/me/preferences", tags=["preferences"])


def _to_out(row: SearchPreferences) -> PreferencesOut:
    # Validé de nouveau à la sortie : une ligne corrompue en base devient une erreur, pas une fuite.
    return PreferencesOut.model_validate(row, from_attributes=True)


@router.get("", response_model=PreferencesOut)
def get_preferences(
    user: CurrentUser = Depends(require_adult), db: Session = Depends(get_db)
) -> PreferencesOut:
    row = service.get_preferences(db, user.user_id)
    if row is None:
        raise ApiError(404, "preferences_not_found", "Preferences not set yet")
    return _to_out(row)


@router.put("", response_model=PreferencesOut)
def put_preferences(
    body: PreferencesIn,
    request: Request,
    user: CurrentUser = Depends(require_adult),
    db: Session = Depends(get_db),
) -> PreferencesOut:
    reference: ReferenceData = request.app.state.reference
    unknown = set(body.sectors) - reference.naf.sector_ids()
    if unknown:
        # Seuls les secteurs de naf_mapping.json existent : on ne devine rien.
        raise ApiError(422, "unknown_sector", "Unknown sector id")
    return _to_out(service.save_preferences(db, user.user_id, body))

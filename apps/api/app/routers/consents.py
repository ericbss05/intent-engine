from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import CurrentUser
from app.domain.reference import ReferenceData
from app.domain.schemas import ConsentChange, ConsentKind, ConsentsOut
from app.routers.deps import require_adult
from app.services import consents as service

router = APIRouter(prefix="/me/consents", tags=["consents"])


@router.get("", response_model=ConsentsOut)
def get_consents(
    request: Request,
    user: CurrentUser = Depends(require_adult),
    db: Session = Depends(get_db),
) -> ConsentsOut:
    reference: ReferenceData = request.app.state.reference
    return ConsentsOut(consents=service.consent_states(db, user.user_id, reference.consent_texts))


@router.put("/{kind}", response_model=ConsentsOut)
def put_consent(
    kind: ConsentKind,
    body: ConsentChange,
    request: Request,
    response: Response,
    user: CurrentUser = Depends(require_adult),
    db: Session = Depends(get_db),
) -> ConsentsOut:
    """Accord ou retrait (à tout moment). `kind` est un type de consentement, pas un utilisateur."""
    reference: ReferenceData = request.app.state.reference
    service.change_consent(
        db, user.user_id, kind, body.granted, body.version_text, reference.consent_texts
    )
    return ConsentsOut(consents=service.consent_states(db, user.user_id, reference.consent_texts))

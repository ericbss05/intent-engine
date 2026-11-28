from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.domain.reference import ConsentTexts, ReferenceData

router = APIRouter(prefix="/reference", tags=["reference"])


class SectorOut(BaseModel):
    id: str
    label: str


def _reference(request: Request) -> ReferenceData:
    reference: ReferenceData = request.app.state.reference
    return reference


# Données publiques et non personnelles (liste de secteurs, textes d'information) :
# pas d'authentification, car l'information RGPD doit être lisible AVANT l'inscription complète.
@router.get("/sectors", response_model=list[SectorOut])
def list_sectors(request: Request) -> list[SectorOut]:
    return [SectorOut(id=s.id, label=s.label) for s in _reference(request).naf.sectors]


@router.get("/consent-texts", response_model=ConsentTexts)
def consent_texts(request: Request) -> ConsentTexts:
    return _reference(request).consent_texts

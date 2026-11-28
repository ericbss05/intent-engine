"""Données de référence versionnées dans le dépôt (data/*.json), validées au démarrage.

Une erreur de format dans un de ces fichiers empêche l'application de démarrer : mieux
vaut une panne visible qu'un questionnaire qui accepte n'importe quoi.
"""

import json
import re
from pathlib import Path

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

# Division (62), groupe/classe (58.2) ou sous-classe (62.01Z) de la NAF rév. 2.
_NAF_PREFIX = re.compile(r"^\d{2}(\.\d{1,2}[A-Z]?)?$")
_SECTOR_ID = re.compile(r"^[a-z][a-z0-9_]{1,59}$")


class Sector(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    label: str
    naf: list[str]

    @field_validator("id")
    @classmethod
    def _id_format(cls, v: str) -> str:
        if not _SECTOR_ID.match(v):
            raise ValueError("invalid sector id")
        return v

    @field_validator("naf")
    @classmethod
    def _naf_format(cls, codes: list[str]) -> list[str]:
        if not codes or len(set(codes)) != len(codes):
            raise ValueError("naf codes must be non-empty and unique")
        for code in codes:
            if not _NAF_PREFIX.match(code):
                raise ValueError(f"invalid NAF code: {code}")
        return codes


class NafMapping(BaseModel):
    version: str
    status: str
    note: str
    sectors: list[Sector]

    @model_validator(mode="after")
    def _unique_ids(self) -> "NafMapping":
        ids = [s.id for s in self.sectors]
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate sector ids")
        return self

    def sector_ids(self) -> set[str]:
        return {s.id for s in self.sectors}


class ConsentText(BaseModel):
    version: str
    title: str
    text: str


class ConsentTexts(BaseModel):
    version_note: str
    privacy_notice: ConsentText
    ai_assist: ConsentText

    def for_kind(self, kind: str) -> ConsentText:
        if kind == "privacy_notice":
            return self.privacy_notice
        if kind == "ai_assist":
            return self.ai_assist
        raise KeyError(kind)


class ReferenceData(BaseModel):
    naf: NafMapping
    consent_texts: ConsentTexts


def load_reference_data(data_dir: Path) -> ReferenceData:
    return ReferenceData(
        naf=NafMapping.model_validate(
            json.loads((data_dir / "naf_mapping.json").read_text(encoding="utf-8"))
        ),
        consent_texts=ConsentTexts.model_validate(
            json.loads((data_dir / "consent_texts.json").read_text(encoding="utf-8"))
        ),
    )

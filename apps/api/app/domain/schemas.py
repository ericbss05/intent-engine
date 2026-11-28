"""Schémas Pydantic des préférences (validation à la frontière : tout ce qui entre est vérifié)."""

import re
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

ContractType = Literal["stage", "alternance"]
# Tranches d'effectif (nombre de salariés).
CompanySize = Literal["1-9", "10-49", "50-249", "250-999", "1000+"]
# Ce qui compte le plus pour l'étudiant (servira au scoring, partie 7). L'ordre = l'importance.
Priority = Literal["sector", "distance", "company_size"]

_POSTCODE = re.compile(r"^\d{5}$")
# Départements : 01-95 (2A/2B pour la Corse) et outre-mer 971-976, 984-989.
_DEPARTMENT = re.compile(r"^(0[1-9]|[1-8]\d|9[0-5]|2A|2B|97[1-6]|98[4-9])$")
_SIREN = re.compile(r"^\d{9}$")
# Pas de caractères de contrôle ni de chevrons : le métier est du texte libre affiché plus tard.
_ROLE = re.compile(r"^[^\x00-\x1f<>]+$")


def _unique(values: list[str]) -> list[str]:
    if len(set(values)) != len(values):
        raise ValueError("duplicate values")
    return values


UniqueList = AfterValidator(_unique)


class Zone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Code postal (5 chiffres) ou département (« 75 », « 2A », « 971 ») : jamais une adresse.
    location: str
    radius_km: Annotated[int, Field(ge=0, le=200)]

    @field_validator("location")
    @classmethod
    def _location_format(cls, v: str) -> str:
        v = v.strip().upper()
        if not (_POSTCODE.match(v) or _DEPARTMENT.match(v)):
            raise ValueError("location must be a 5-digit postcode or a department code")
        return v


def _normalize_siren(value: str) -> str:
    cleaned = value.replace(" ", "")
    if not _SIREN.match(cleaned):
        raise ValueError("SIREN must be 9 digits")
    return cleaned


Siren = Annotated[str, AfterValidator(_normalize_siren)]


class PreferencesIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    contract_type: ContractType
    # Fourchette volontairement large (stage ≈ 1–6 mois, alternance ≈ 6–36 mois).
    duration_months: Annotated[int, Field(ge=1, le=36)]
    target_role: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)
    ]
    sectors: Annotated[list[str], Field(min_length=1, max_length=10), UniqueList]
    zone: Zone
    company_size: Annotated[list[CompanySize], Field(min_length=1, max_length=5), UniqueList]
    priorities: Annotated[list[Priority], Field(max_length=3), UniqueList] = []
    excluded_sirens: Annotated[list[Siren], Field(max_length=200), UniqueList] = []

    @field_validator("target_role")
    @classmethod
    def _role_chars(cls, v: str) -> str:
        if not _ROLE.match(v):
            raise ValueError("invalid characters")
        return v


class PreferencesOut(PreferencesIn):
    updated_at: datetime


ConsentKind = Literal["privacy_notice", "ai_assist"]


class ConsentChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    granted: bool
    # Version du texte que l'étudiant a VU : refusée si ce n'est plus la version en vigueur.
    version_text: Annotated[str, StringConstraints(min_length=1, max_length=32)]


class ConsentState(BaseModel):
    kind: ConsentKind
    granted: bool
    version_text: str | None
    recorded_at: datetime | None
    current_version: str


class ConsentsOut(BaseModel):
    consents: list[ConsentState]

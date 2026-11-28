"""Modèles SQLAlchemy. Schéma = docs/03-modele-de-donnees.md.

R2 (minimisation) : AUCUNE colonne pour photo, date de naissance, nationalité, situation
familiale, santé, adresse exacte, téléphone personnel. Un test garde une liste blanche.
Toutes les dates sont en UTC.
"""

from datetime import UTC, datetime
from typing import Any, Literal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Noms de contraintes prévisibles : nécessaires pour des migrations Alembic propres.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

ConsentKind = Literal["ai_assist", "privacy_notice"]


def utcnow() -> datetime:
    return datetime.now(UTC)


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UserProfile(Base):
    __tablename__ = "user_profile"

    # Identifiant Clerk (ex. « user_2abc… »). Ni email ni nom stockés ici.
    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # Renseigné quand l'étudiant coche « j'ai 18 ans ou plus ». On ne consigne jamais l'inverse.
    adult_confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Décoché par défaut (R12). Le journal détaillé est dans `consents`.
    ai_assist_consent: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("false")
    )
    ai_assist_consent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Consent(Base):
    __tablename__ = "consents"
    __table_args__ = (Index("ix_consents_user_id_kind", "user_id", "kind"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # ON DELETE CASCADE : supprimer le profil supprime les consentements (R4).
    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_profile.user_id", ondelete="CASCADE"), index=False
    )
    kind: Mapped[str] = mapped_column(String(32))
    granted: Mapped[bool] = mapped_column(Boolean)
    version_text: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class SearchPreferences(Base):
    """Réponses au questionnaire (une ligne par étudiant, remplacée à chaque sauvegarde)."""

    __tablename__ = "search_preferences"
    __table_args__ = (
        CheckConstraint("contract_type in ('stage', 'alternance')", name="contract_type"),
        CheckConstraint("duration_months between 1 and 36", name="duration_months"),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("user_profile.user_id", ondelete="CASCADE"), primary_key=True
    )
    contract_type: Mapped[str] = mapped_column(String(16))
    duration_months: Mapped[int] = mapped_column(Integer)
    target_role: Mapped[str] = mapped_column(String(100))
    # Identifiants de secteurs de data/naf_mapping.json (ex. ["informatique_telecoms"]).
    sectors: Mapped[list[str]] = mapped_column(JSONB)
    # {"location": "75" ou "75011", "radius_km": 30} : zone grossière, jamais une adresse exacte.
    zone: Mapped[dict[str, Any]] = mapped_column(JSONB)
    company_size: Mapped[list[str]] = mapped_column(JSONB)
    priorities: Mapped[list[str]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    # SIREN (9 chiffres) d'entreprises déjà contactées : on ne les proposera pas.
    excluded_sirens: Mapped[list[str]] = mapped_column(JSONB, server_default=text("'[]'::jsonb"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

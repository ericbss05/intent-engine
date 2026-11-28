"""Couche d'accès aux données d'un étudiant.

RÈGLE (R3, CLAUDE.md §6.3) : chaque fonction prend `user_id` et filtre dessus. Les routes
n'utilisent JAMAIS les modèles directement, et `user_id` vient du jeton vérifié, pas de
la requête. Cette structure permet d'ajouter plus tard la sécurité au niveau des lignes
(RLS PostgreSQL) sans changer les appelants.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import delete, inspect, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.domain.models import Base, Consent, SearchPreferences, UserProfile, utcnow

# Toute table qui contient des données d'un étudiant DOIT figurer ici : elle est alors
# incluse dans l'export. Un test échoue si une table avec `user_id` est oubliée.
# Les parties suivantes ajoutent leurs modèles (préférences, profils CV, recherches…).
USER_OWNED_MODELS: tuple[type[Base], ...] = (UserProfile, Consent, SearchPreferences)

EXPORT_FORMAT_VERSION = 1


def get_profile(db: Session, user_id: str) -> UserProfile | None:
    return db.scalars(select(UserProfile).where(UserProfile.user_id == user_id)).first()


def ensure_profile(db: Session, user_id: str) -> UserProfile:
    """Crée le profil s'il n'existe pas (idempotent : le webhook peut arriver en double)."""
    db.execute(pg_insert(UserProfile).values(user_id=user_id).on_conflict_do_nothing())
    db.flush()
    profile = get_profile(db, user_id)
    if profile is None:  # pragma: no cover - impossible après l'insertion ci-dessus
        raise RuntimeError("Profile creation failed")
    return profile


def touch_last_active(db: Session, user_id: str) -> None:
    profile = get_profile(db, user_id)
    if profile is not None:
        profile.last_active_at = utcnow()


def confirm_adult(db: Session, user_id: str) -> UserProfile:
    """Journalise « 18 ans ou plus » (R13). Rien n'est consigné pour un refus."""
    profile = ensure_profile(db, user_id)
    if profile.adult_confirmed_at is None:
        profile.adult_confirmed_at = utcnow()
    return profile


def is_adult_confirmed(db: Session, user_id: str) -> bool:
    profile = get_profile(db, user_id)
    return profile is not None and profile.adult_confirmed_at is not None


def record_consent(
    db: Session, user_id: str, kind: str, granted: bool, version_text: str
) -> Consent:
    """Ajoute une ligne au journal des consentements (jamais de modification d'une ligne)."""
    ensure_profile(db, user_id)
    consent = Consent(user_id=user_id, kind=kind, granted=granted, version_text=version_text)
    db.add(consent)
    db.flush()
    return consent


def list_consents(db: Session, user_id: str) -> list[Consent]:
    return list(
        db.scalars(select(Consent).where(Consent.user_id == user_id).order_by(Consent.id)).all()
    )


def _serialize(row: Base) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for column in inspect(type(row)).columns:
        value = getattr(row, column.key)
        out[column.key] = value.isoformat() if isinstance(value, datetime) else value
    return out


def export_user_data(db: Session, user_id: str) -> dict[str, Any]:
    """Toutes les données de l'étudiant, table par table (droit d'accès / portabilité, R4)."""
    tables: dict[str, list[dict[str, Any]]] = {}
    for model in USER_OWNED_MODELS:
        user_id_col = model.__table__.c["user_id"]
        rows = db.scalars(select(model).where(user_id_col == user_id)).all()
        tables[model.__tablename__] = [_serialize(r) for r in rows]
    return {
        "format_version": EXPORT_FORMAT_VERSION,
        "exported_at": utcnow().isoformat(),
        "tables": tables,
    }


def delete_user_data(db: Session, user_id: str) -> bool:
    """Supprime toutes les données de l'étudiant (idempotent). True si quelque chose existait."""
    # Les tables enfants sont supprimées par ON DELETE CASCADE depuis user_profile ;
    # on supprime explicitement les autres tables à user_id par sécurité.
    existed = False
    for model in reversed(USER_OWNED_MODELS):
        user_id_col = model.__table__.c["user_id"]
        result = db.execute(delete(model).where(user_id_col == user_id))
        existed = existed or bool(result.rowcount)  # type: ignore[attr-defined]
    db.flush()
    return existed

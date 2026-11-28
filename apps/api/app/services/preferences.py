"""Accès aux préférences de recherche d'un étudiant (toujours filtré par `user_id`)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.models import SearchPreferences, utcnow
from app.domain.schemas import PreferencesIn
from app.services.user_data import ensure_profile


def get_preferences(db: Session, user_id: str) -> SearchPreferences | None:
    return db.scalars(select(SearchPreferences).where(SearchPreferences.user_id == user_id)).first()


def save_preferences(db: Session, user_id: str, data: PreferencesIn) -> SearchPreferences:
    """Remplace les préférences (création ou mise à jour)."""
    ensure_profile(db, user_id)
    row = get_preferences(db, user_id)
    if row is None:
        row = SearchPreferences(user_id=user_id)
        db.add(row)
    row.contract_type = data.contract_type
    row.duration_months = data.duration_months
    row.target_role = data.target_role
    row.sectors = list(data.sectors)
    row.zone = data.zone.model_dump()
    row.company_size = list(data.company_size)
    row.priorities = list(data.priorities)
    row.excluded_sirens = list(data.excluded_sirens)
    row.updated_at = utcnow()
    db.flush()
    return row

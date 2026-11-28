"""Environnement Alembic : lit l'URL dans les variables d'environnement (jamais en dur).

Les migrations utilisent la connexion DIRECTE de Neon (DATABASE_URL_DIRECT) si elle existe :
le pooler PgBouncer n'est pas adapté aux changements de schéma.
"""

import os

from sqlalchemy import create_engine

from alembic import context
from app.core.config import Settings
from app.core.db import normalize_url
from app.domain.models import Base

target_metadata = Base.metadata


def _database_url() -> str:
    # Les tests fournissent l'URL explicitement (base jetable) via cette variable.
    override = os.environ.get("ALEMBIC_DATABASE_URL")
    if override:
        return normalize_url(override)
    settings = Settings()
    secret = settings.database_url_direct or settings.database_url
    if secret is None or not secret.get_secret_value():
        raise RuntimeError("DATABASE_URL (or DATABASE_URL_DIRECT) is not set")
    return normalize_url(secret.get_secret_value())


def run_migrations_online() -> None:
    engine = create_engine(_database_url())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    raise RuntimeError("Offline mode is not supported")
run_migrations_online()

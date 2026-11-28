"""Connexion à PostgreSQL (SQLAlchemy 2, mode synchrone).

Neon fournit deux adresses : une « poolée » (PgBouncer, pour l'application, pensée pour
le serverless) et une « directe » (pour les migrations). PgBouncer en mode transaction
ne supporte pas les requêtes préparées côté serveur : on les désactive (prepare_threshold=None).
"""

from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings


def normalize_url(url: str) -> str:
    # Neon donne « postgresql://… » ; on impose le pilote psycopg 3.
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    return url


def make_engine(url: str) -> Engine:
    return create_engine(
        normalize_url(url),
        pool_pre_ping=True,  # détecte les connexions coupées (Neon met la base en veille)
        pool_size=5,
        max_overflow=5,
        pool_recycle=300,
        connect_args={"prepare_threshold": None},
    )


_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def init_db(settings: Settings) -> None:
    global _engine, _session_factory
    if settings.database_url is None:
        return  # tests : le moteur est injecté par les fixtures
    _engine = make_engine(settings.database_url.get_secret_value())
    _session_factory = sessionmaker(_engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """Dépendance FastAPI : une session par requête, validée ou annulée proprement."""
    if _session_factory is None:
        raise RuntimeError("Database is not configured")
    with _session_factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise

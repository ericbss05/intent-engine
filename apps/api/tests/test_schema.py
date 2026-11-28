"""R2 (minimisation du schéma), migrations, et garde-fou de l'export (R4)."""

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import Engine, inspect

from app.domain.models import Base
from app.services.user_data import USER_OWNED_MODELS
from tests.conftest import run_alembic

# Liste blanche : ajouter une colonne exige de modifier ce test (donc d'y réfléchir).
ALLOWED_COLUMNS: dict[str, set[str]] = {
    "user_profile": {
        "user_id",
        "created_at",
        "adult_confirmed_at",
        "ai_assist_consent",
        "ai_assist_consent_at",
        "last_active_at",
    },
    "consents": {"id", "user_id", "kind", "granted", "version_text", "created_at"},
    "search_preferences": {
        "user_id",
        "contract_type",
        "duration_months",
        "target_role",
        "sectors",
        "zone",
        "company_size",
        "priorities",
        "excluded_sirens",
        "updated_at",
    },
}

FORBIDDEN_WORDS = (
    "photo", "birth", "naissance", "nationality", "nationalite", "marital", "family",
    "health", "sante", "handicap", "religion", "address", "adresse", "phone", "telephone",
    "email", "name", "nom", "cv_text", "raw_text", "pdf",
)  # fmt: skip


def test_columns_match_whitelist() -> None:
    actual = {t.name: {c.name for c in t.columns} for t in Base.metadata.sorted_tables}
    assert actual == ALLOWED_COLUMNS


def test_no_forbidden_column_name() -> None:
    for table in Base.metadata.sorted_tables:
        for column in table.columns:
            assert not any(w in column.name.lower() for w in FORBIDDEN_WORDS), column.name


def test_every_user_table_is_in_export_registry() -> None:
    user_tables = {t.name for t in Base.metadata.sorted_tables if "user_id" in t.c}
    registered = {m.__tablename__ for m in USER_OWNED_MODELS}
    assert user_tables == registered, "A table with user_id is missing from USER_OWNED_MODELS"


def test_migrated_database_matches_models(engine: Engine) -> None:
    # Si les modèles changent sans migration, cette comparaison trouve une différence.
    with engine.connect() as conn:
        diff = compare_metadata(MigrationContext.configure(conn), Base.metadata)
    assert diff == []


def test_consents_foreign_key_cascades(engine: Engine) -> None:
    fks = inspect(engine).get_foreign_keys("consents")
    assert fks[0]["options"]["ondelete"] == "CASCADE"


def test_migration_downgrade_and_upgrade_roundtrip(engine: Engine) -> None:
    run_alembic("downgrade", "base")
    assert "user_profile" not in inspect(engine).get_table_names()
    run_alembic("upgrade", "head")
    assert {"user_profile", "consents", "search_preferences"} <= set(
        inspect(engine).get_table_names()
    )

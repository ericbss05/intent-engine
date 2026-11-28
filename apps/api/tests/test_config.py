import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_wildcard_origin_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(api_allowed_origins="*")


def test_origins_are_split_and_trimmed() -> None:
    settings = Settings(api_allowed_origins="https://a.example, https://b.example")
    assert settings.allowed_origins == ["https://a.example", "https://b.example"]


def test_invalid_log_level_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings.model_validate({"log_level": "verbose"})


def test_production_requires_database_and_clerk_settings() -> None:
    with pytest.raises(ValidationError) as exc:
        Settings(app_env="production", _env_file=None)
    message = str(exc.value)
    for name in ("DATABASE_URL", "CLERK_JWT_ISSUER", "CLERK_WEBHOOK_SECRET", "CLERK_SECRET_KEY"):
        assert name in message


def test_production_accepts_complete_settings() -> None:
    settings = Settings(
        app_env="production",
        database_url="postgresql://u:p@host/db",
        clerk_jwt_issuer="https://x.clerk.accounts.dev/",
        clerk_webhook_secret="whsec_dGVzdA==",
        clerk_secret_key="sk_test_fake",
        _env_file=None,
    )
    assert settings.clerk_jwt_issuer == "https://x.clerk.accounts.dev"


def test_issuer_must_be_https() -> None:
    with pytest.raises(ValidationError):
        Settings(app_env="test", clerk_jwt_issuer="http://insecure.example", _env_file=None)


def test_secrets_are_not_printed() -> None:
    settings = Settings(
        app_env="test", database_url="postgresql://u:topsecret@h/db", _env_file=None
    )
    assert "topsecret" not in repr(settings)

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

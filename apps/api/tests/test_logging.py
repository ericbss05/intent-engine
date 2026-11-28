import json
import logging

from app.core.logging import JsonFormatter


def make_record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, "request", None, None)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_allowed_fields_are_kept() -> None:
    line = JsonFormatter().format(make_record(method="GET", path="/health", status_code=200))
    data = json.loads(line)
    assert data["method"] == "GET"
    assert data["status_code"] == 200


def test_personal_fields_are_dropped() -> None:
    line = JsonFormatter().format(make_record(email="a@b.fr", cv_text="secret", path="/x"))
    data = json.loads(line)
    assert "email" not in data
    assert "cv_text" not in data
    assert "a@b.fr" not in line

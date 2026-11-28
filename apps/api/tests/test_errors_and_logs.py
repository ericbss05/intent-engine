import logging
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient

from tests.conftest import auth, webhook_headers

MakeToken = Callable[..., str]


def test_validation_error_does_not_echo_input(client: TestClient, make_token: MakeToken) -> None:
    response = client.post(
        "/me/adult-confirmation",
        json={"confirmed": "secret-personal-value@example.com"},
        headers=auth(make_token()),
    )
    assert response.status_code == 422
    body = response.json()
    assert set(body) == {"code", "message"}
    assert "secret-personal-value" not in response.text


def test_logs_contain_no_personal_data(
    client: TestClient, make_token: MakeToken, caplog: pytest.LogCaptureFixture
) -> None:
    body = (
        b'{"type":"user.created","data":{"id":"user_L1",'
        b'"email_addresses":[{"email_address":"jean.dupont@example.com"}],"first_name":"Jean"}}'
    )
    with caplog.at_level(logging.DEBUG):
        client.post("/webhooks/clerk", content=body, headers=webhook_headers(body))
        client.get("/me?email=jean.dupont@example.com", headers=auth(make_token("user_L1")))
    # On ne regarde que les logs de NOTRE application : le client de test (httpx2) logge
    # lui-même l'URL complète, ce qui n'existe pas côté serveur.
    ours = [r for r in caplog.records if r.name.startswith("app.")]
    assert ours, "expected application log records"
    text = " ".join(f"{r.getMessage()} {r.__dict__}" for r in ours)
    assert "jean.dupont" not in text
    assert "Jean" not in text

"""Jetons factices : le backend accepte un jeton valide et refuse tout le reste."""

from collections.abc import Callable
from datetime import timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

from tests.conftest import auth

MakeToken = Callable[..., str]


def test_no_token_is_401(client: TestClient) -> None:
    response = client.get("/me")
    assert response.status_code == 401
    assert response.json()["code"] == "missing_token"


def test_valid_token_is_accepted(client: TestClient, make_token: MakeToken) -> None:
    client.post("/me/adult-confirmation", json={"confirmed": True}, headers=auth(make_token()))
    assert client.get("/me", headers=auth(make_token())).status_code == 200


@pytest.mark.parametrize(
    "overrides",
    [
        {"exp": 1},  # expiré
        {"iss": "https://evil.example"},  # mauvais émetteur
        {"azp": "https://evil.example"},  # jeton obtenu par un autre site
        {"sub": None},  # pas d'identité
    ],
)
def test_invalid_claims_are_401(
    client: TestClient, make_token: MakeToken, overrides: dict[str, object]
) -> None:
    response = client.get("/me", headers=auth(make_token(**overrides)))
    assert response.status_code == 401


def test_token_signed_with_another_key_is_401(client: TestClient, make_token: MakeToken) -> None:
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    assert client.get("/me", headers=auth(make_token(key=other))).status_code == 401


def test_hs256_token_is_refused(client: TestClient, make_token: MakeToken) -> None:
    # Attaque classique : signer avec un secret symétrique en espérant que le serveur l'accepte.
    token = make_token(key="x" * 64, algorithm="HS256")
    assert client.get("/me", headers=auth(token)).status_code == 401


def test_unsigned_token_is_refused(client: TestClient) -> None:
    token = jwt.encode({"sub": "user_A"}, key="", algorithm="none")
    assert client.get("/me", headers=auth(token)).status_code == 401


def test_garbage_token_is_401(client: TestClient) -> None:
    assert client.get("/me", headers=auth("not-a-jwt")).status_code == 401


def test_admin_route_requires_role(client: TestClient, make_token: MakeToken) -> None:
    assert client.get("/admin/status").status_code == 401
    forbidden = client.get("/admin/status", headers=auth(make_token("user_A")))
    assert forbidden.status_code == 403
    assert forbidden.json()["code"] == "forbidden"
    wrong_role = client.get("/admin/status", headers=auth(make_token("user_A", role="student")))
    assert wrong_role.status_code == 403
    ok = client.get("/admin/status", headers=auth(make_token("user_B", role="admin")))
    assert ok.status_code == 200
    assert ok.json() == {"status": "ok"}


def test_role_cannot_be_forged_through_headers_or_query(
    client: TestClient, make_token: MakeToken
) -> None:
    response = client.get(
        "/admin/status?role=admin",
        headers={**auth(make_token("user_A")), "X-Role": "admin"},
    )
    assert response.status_code == 403


def test_unconfigured_auth_fails_closed() -> None:
    # Sans vérificateur configuré, aucune route protégée n'est ouverte.
    from app.core.config import Settings
    from app.main import create_app

    app = create_app(Settings(app_env="test", _env_file=None))
    assert TestClient(app).get("/me", headers={"Authorization": "Bearer abc"}).status_code == 503


def test_token_expiry_leeway_is_small(client: TestClient, make_token: MakeToken) -> None:
    import time

    expired = make_token(exp=int(time.time()) - int(timedelta(minutes=2).total_seconds()))
    assert client.get("/me", headers=auth(expired)).status_code == 401

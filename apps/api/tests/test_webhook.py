import json
import time

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.webhook import sign, verify_signature
from app.services import user_data
from tests.conftest import WEBHOOK_SECRET, webhook_headers


def _body(event_type: str, user_id: str) -> bytes:
    # Données factices ; le vrai webhook contient emails et noms (qu'on ne stocke pas).
    return json.dumps(
        {
            "type": event_type,
            "data": {"id": user_id, "email_addresses": [{"email_address": "x@y.z"}]},
        }
    ).encode()


def test_signature_unit_cases() -> None:
    body = b'{"a":1}'
    now = time.time()
    sig = sign(WEBHOOK_SECRET, "m1", str(int(now)), body)
    assert verify_signature(WEBHOOK_SECRET, "m1", str(int(now)), f"v1,{sig}", body, now)
    # corps modifié, mauvais id, mauvaise version, horodatage trop ancien ou invalide
    assert not verify_signature(WEBHOOK_SECRET, "m1", str(int(now)), f"v1,{sig}", b"{}", now)
    assert not verify_signature(WEBHOOK_SECRET, "m2", str(int(now)), f"v1,{sig}", body, now)
    assert not verify_signature(WEBHOOK_SECRET, "m1", str(int(now)), f"v2,{sig}", body, now)
    assert not verify_signature(WEBHOOK_SECRET, "m1", str(int(now)), f"v1,{sig}", body, now + 3600)
    assert not verify_signature(WEBHOOK_SECRET, "m1", "abc", f"v1,{sig}", body, now)
    # plusieurs signatures (rotation de secret) : une bonne suffit
    assert verify_signature(WEBHOOK_SECRET, "m1", str(int(now)), f"v1,AAAA v1,{sig}", body, now)


def test_user_created_creates_profile_idempotently(client: TestClient, db: Session) -> None:
    body = _body("user.created", "user_W1")
    for _ in range(2):  # rejeu : pas de doublon, pas d'erreur
        response = client.post("/webhooks/clerk", content=body, headers=webhook_headers(body))
        assert response.status_code == 200
    profile = user_data.get_profile(db, "user_W1")
    assert profile is not None
    assert profile.adult_confirmed_at is None  # la case 18+ n'est pas cochée automatiquement
    assert profile.ai_assist_consent is False


def test_user_deleted_removes_everything(client: TestClient, db: Session) -> None:
    user_data.confirm_adult(db, "user_W2")
    user_data.record_consent(db, "user_W2", "privacy_notice", True, "v1")
    db.commit()
    body = _body("user.deleted", "user_W2")
    assert (
        client.post("/webhooks/clerk", content=body, headers=webhook_headers(body)).status_code
        == 200
    )
    db.expire_all()
    assert user_data.get_profile(db, "user_W2") is None
    assert user_data.list_consents(db, "user_W2") == []


def test_bad_signature_is_rejected_and_changes_nothing(client: TestClient, db: Session) -> None:
    user_data.ensure_profile(db, "user_W3")
    db.commit()
    body = _body("user.deleted", "user_W3")
    headers = webhook_headers(body)
    headers["svix-signature"] = "v1,AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
    assert client.post("/webhooks/clerk", content=body, headers=headers).status_code == 400
    # sans en-têtes du tout
    assert client.post("/webhooks/clerk", content=body).status_code == 400
    # signature valide mais corps différent (falsifié en route)
    forged = _body("user.deleted", "user_W3-other")
    assert (
        client.post("/webhooks/clerk", content=forged, headers=webhook_headers(body)).status_code
        == 400
    )
    db.expire_all()
    assert user_data.get_profile(db, "user_W3") is not None


def test_old_message_is_rejected(client: TestClient) -> None:
    body = _body("user.created", "user_W4")
    old = webhook_headers(body, ts=int(time.time()) - 3600)
    assert client.post("/webhooks/clerk", content=body, headers=old).status_code == 400


def test_unknown_event_is_acknowledged_without_effect(client: TestClient, db: Session) -> None:
    body = _body("session.created", "user_W5")
    assert (
        client.post("/webhooks/clerk", content=body, headers=webhook_headers(body)).status_code
        == 200
    )
    assert user_data.get_profile(db, "user_W5") is None


def test_malformed_signed_payload_is_400(client: TestClient) -> None:
    body = b'{"type": 1}'
    assert (
        client.post("/webhooks/clerk", content=body, headers=webhook_headers(body)).status_code
        == 400
    )


def test_oversized_payload_is_rejected(client: TestClient) -> None:
    body = b"x" * (65 * 1024)
    assert (
        client.post("/webhooks/clerk", content=body, headers=webhook_headers(body)).status_code
        == 413
    )

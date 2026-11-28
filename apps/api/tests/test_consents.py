"""Consentements : décoché par défaut, journalisé avec la version du texte, retirable, garde IA."""

from collections.abc import Callable

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from httpx2 import Response
from sqlalchemy.orm import Session

from app.core.errors import ApiError
from app.core.security import CurrentUser
from app.domain.reference import ConsentTexts
from app.services import consents as service
from app.services import user_data
from app.services.ai_guard import ai_consent_required, has_ai_consent, require_ai_consent
from tests.conftest import auth

MakeToken = Callable[..., str]


def _adult(client: TestClient, token: str) -> dict[str, str]:
    headers = auth(token)
    client.post("/me/adult-confirmation", json={"confirmed": True}, headers=headers)
    return headers


def _versions(client: TestClient) -> dict[str, str]:
    texts = client.get("/reference/consent-texts").json()
    return {
        "privacy_notice": texts["privacy_notice"]["version"],
        "ai_assist": texts["ai_assist"]["version"],
    }


def _put(
    client: TestClient, headers: dict[str, str], kind: str, granted: bool, version: str
) -> Response:
    return client.put(
        f"/me/consents/{kind}", json={"granted": granted, "version_text": version}, headers=headers
    )


def _state(client: TestClient, headers: dict[str, str], kind: str) -> dict[str, object]:
    states = client.get("/me/consents", headers=headers).json()["consents"]
    return next(s for s in states if s["kind"] == kind)


def test_public_reference_endpoints(client: TestClient) -> None:
    texts = client.get("/reference/consent-texts")
    assert texts.status_code == 200
    assert "Option 1" in texts.json()["ai_assist"]["text"]
    sectors = client.get("/reference/sectors").json()
    assert 15 <= len(sectors) <= 25
    assert all(set(s) == {"id", "label"} for s in sectors)  # pas de codes NAF exposés inutilement


def test_ai_consent_is_off_by_default(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    state = _state(client, headers, "ai_assist")
    assert state["granted"] is False and state["version_text"] is None
    assert client.get("/me", headers=headers).json()["ai_assist_consent"] is False


def test_consent_routes_need_auth_and_adult(client: TestClient, make_token: MakeToken) -> None:
    assert client.get("/me/consents").status_code == 401
    headers = auth(make_token("user_A"))  # 18+ non confirmé
    assert client.get("/me/consents", headers=headers).status_code == 403


def test_grant_is_logged_with_text_version_then_withdrawn(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = _adult(client, make_token("user_A"))
    version = _versions(client)["ai_assist"]

    assert _put(client, headers, "ai_assist", True, version).status_code == 200
    state = _state(client, headers, "ai_assist")
    assert state["granted"] is True and state["version_text"] == version
    assert client.get("/me", headers=headers).json()["ai_assist_consent"] is True
    assert has_ai_consent(db, "user_A")

    assert _put(client, headers, "ai_assist", False, version).status_code == 200  # retrait
    assert _state(client, headers, "ai_assist")["granted"] is False
    assert client.get("/me", headers=headers).json()["ai_assist_consent"] is False
    db.expire_all()
    assert not has_ai_consent(db, "user_A")

    # Le journal garde les DEUX lignes (accord puis retrait), jamais de modification.
    rows = [c for c in user_data.list_consents(db, "user_A") if c.kind == "ai_assist"]
    assert [(c.granted, c.version_text) for c in rows] == [(True, version), (False, version)]
    profile = user_data.get_profile(db, "user_A")
    assert profile is not None and profile.ai_assist_consent_at is not None


def test_repeating_the_same_choice_adds_no_row(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = _adult(client, make_token("user_A"))
    version = _versions(client)["ai_assist"]
    for _ in range(3):
        _put(client, headers, "ai_assist", True, version)
    assert len([c for c in user_data.list_consents(db, "user_A") if c.kind == "ai_assist"]) == 1


def test_initial_refusal_writes_nothing(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = _adult(client, make_token("user_A"))
    assert (
        _put(client, headers, "ai_assist", False, _versions(client)["ai_assist"]).status_code == 200
    )
    assert user_data.list_consents(db, "user_A") == []


def test_outdated_text_version_is_refused(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    response = _put(client, headers, "ai_assist", True, "old-version")
    assert response.status_code == 409
    assert response.json()["code"] == "consent_text_outdated"
    assert _state(client, headers, "ai_assist")["granted"] is False


def test_privacy_notice_can_only_be_acknowledged(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    version = _versions(client)["privacy_notice"]
    assert _put(client, headers, "privacy_notice", False, version).status_code == 422
    assert _put(client, headers, "privacy_notice", True, version).status_code == 200
    state = _state(client, headers, "privacy_notice")
    assert state["granted"] is True and state["version_text"] == version


def test_unknown_consent_kinds_are_refused(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    for kind in ("model_training", "training", "ml", "marketing"):
        # ADR 0007 : aucun consentement « entraînement de modèle » n'existe.
        assert _put(client, headers, kind, True, "x").status_code == 422


def test_consents_are_per_user(client: TestClient, make_token: MakeToken, db: Session) -> None:
    a = _adult(client, make_token("user_A"))
    b = _adult(client, make_token("user_B"))
    _put(client, a, "ai_assist", True, _versions(client)["ai_assist"])
    assert _state(client, b, "ai_assist")["granted"] is False
    assert has_ai_consent(db, "user_A") and not has_ai_consent(db, "user_B")


# --- Garde : sans consentement, aucun appel IA possible


def test_guard_blocks_without_consent_and_after_withdrawal(db: Session) -> None:
    user_data.confirm_adult(db, "user_A")
    with pytest.raises(ApiError) as exc:
        require_ai_consent(db, "user_A")
    assert exc.value.code == "ai_consent_required" and exc.value.status_code == 403

    texts = _texts()
    version = texts.ai_assist.version
    service.change_consent(db, "user_A", "ai_assist", True, version, texts)
    require_ai_consent(db, "user_A")  # autorisé
    service.change_consent(db, "user_A", "ai_assist", False, version, texts)
    with pytest.raises(ApiError):
        require_ai_consent(db, "user_A")  # le retrait est immédiat


def test_guard_is_per_user(db: Session) -> None:
    texts = _texts()
    user_data.confirm_adult(db, "user_A")
    user_data.confirm_adult(db, "user_B")
    service.change_consent(db, "user_B", "ai_assist", True, texts.ai_assist.version, texts)
    with pytest.raises(ApiError):
        require_ai_consent(db, "user_A")


def test_guard_dependency_protects_a_future_ai_route(
    app: FastAPI, client: TestClient, make_token: MakeToken
) -> None:
    called = {"count": 0}

    @app.post("/_test/ai-analysis")
    def analysis(user: CurrentUser = Depends(ai_consent_required)) -> dict[str, str]:
        called["count"] += 1  # ici, plus tard : l'appel au LLMClient
        return {"ok": user.user_id}

    headers = _adult(client, make_token("user_A"))
    blocked = client.post("/_test/ai-analysis", headers=headers)
    assert blocked.status_code == 403 and called["count"] == 0
    _put(client, headers, "ai_assist", True, _versions(client)["ai_assist"])
    assert client.post("/_test/ai-analysis", headers=headers).status_code == 200
    _put(client, headers, "ai_assist", False, _versions(client)["ai_assist"])
    assert client.post("/_test/ai-analysis", headers=headers).status_code == 403
    assert called["count"] == 1


def _texts() -> ConsentTexts:
    from app.core.config import Settings
    from app.domain.reference import load_reference_data

    return load_reference_data(
        Settings(app_env="test", _env_file=None).resolved_data_dir
    ).consent_texts

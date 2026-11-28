"""R3 : l'étudiant A ne voit, ne modifie et ne supprime jamais les données de B."""

from collections.abc import Callable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services import user_data
from tests.conftest import auth

MakeToken = Callable[..., str]


def _seed(db: Session) -> None:
    for uid in ("user_A", "user_B"):
        user_data.confirm_adult(db, uid)
        user_data.record_consent(db, uid, "privacy_notice", True, f"v1-{uid}")
    db.commit()


def test_service_reads_are_scoped(db: Session) -> None:
    _seed(db)
    assert [c.version_text for c in user_data.list_consents(db, "user_A")] == ["v1-user_A"]
    assert user_data.get_profile(db, "user_A") is not None
    assert user_data.get_profile(db, "user_A").user_id == "user_A"  # type: ignore[union-attr]
    exported = user_data.export_user_data(db, "user_A")
    dumped = str(exported)
    assert "user_B" not in dumped and "v1-user_B" not in dumped


def test_service_writes_are_scoped(db: Session) -> None:
    user_data.ensure_profile(db, "user_A")
    user_data.ensure_profile(db, "user_B")
    user_data.confirm_adult(db, "user_A")
    user_data.record_consent(db, "user_A", "ai_assist", True, "v1")
    db.commit()
    b = user_data.get_profile(db, "user_B")
    assert b is not None and b.adult_confirmed_at is None
    assert user_data.list_consents(db, "user_B") == []


def test_service_delete_is_scoped(db: Session) -> None:
    _seed(db)
    assert user_data.delete_user_data(db, "user_A") is True
    db.commit()
    assert user_data.get_profile(db, "user_A") is None
    assert user_data.get_profile(db, "user_B") is not None
    assert len(user_data.list_consents(db, "user_B")) == 1


def test_http_each_user_sees_only_own_data(client: TestClient, make_token: MakeToken) -> None:
    for uid in ("user_A", "user_B"):
        client.post(
            "/me/adult-confirmation", json={"confirmed": True}, headers=auth(make_token(uid))
        )
    export_a = client.get("/me/export", headers=auth(make_token("user_A"))).json()
    rows = export_a["tables"]["user_profile"]
    assert [r["user_id"] for r in rows] == ["user_A"]
    assert "user_B" not in str(export_a)


def test_http_delete_me_never_touches_other_user(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    _seed(db)
    assert client.delete("/me", headers=auth(make_token("user_A"))).status_code == 204
    db.expire_all()
    assert user_data.get_profile(db, "user_A") is None
    assert user_data.get_profile(db, "user_B") is not None


def test_no_route_takes_a_user_id_from_the_request(client: TestClient) -> None:
    # L'identité vient uniquement du jeton : aucune route ne doit avoir de paramètre user_id.
    schema_paths = client.app.openapi()["paths"]  # type: ignore[attr-defined]
    for path, methods in schema_paths.items():
        assert "user_id" not in path
        for operation in methods.values():
            for param in operation.get("parameters", []):
                assert "user" not in param["name"].lower()
            assert "user_id" not in str(operation.get("requestBody", ""))

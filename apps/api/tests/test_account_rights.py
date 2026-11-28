"""R4 : export complet, suppression en cascade table par table, 18+ (R13)."""

from collections.abc import Callable

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.security import CurrentUser
from app.domain.models import Base
from app.routers.deps import require_adult
from app.services import user_data
from tests.conftest import FakeIdentity, auth

MakeToken = Callable[..., str]


def _populate(db: Session, uid: str) -> None:
    user_data.confirm_adult(db, uid)
    user_data.record_consent(db, uid, "privacy_notice", True, "v1")
    user_data.record_consent(db, uid, "ai_assist", False, "v1")
    db.commit()


def test_export_contains_all_user_tables_and_rows(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    _populate(db, "user_A")
    response = client.get("/me/export", headers=auth(make_token("user_A")))
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store"
    data = response.json()
    assert data["format_version"] == 1
    expected_tables = {t.name for t in Base.metadata.sorted_tables if "user_id" in t.c}
    assert set(data["tables"]) == expected_tables
    assert len(data["tables"]["user_profile"]) == 1
    assert len(data["tables"]["consents"]) == 2
    assert data["tables"]["user_profile"][0]["adult_confirmed_at"] is not None


def test_export_for_unknown_user_is_empty_not_error(
    client: TestClient, make_token: MakeToken
) -> None:
    data = client.get("/me/export", headers=auth(make_token("user_new"))).json()
    assert all(rows == [] for rows in data["tables"].values())


def test_delete_cascades_table_by_table(
    client: TestClient, make_token: MakeToken, db: Session, identity: FakeIdentity
) -> None:
    _populate(db, "user_A")
    _populate(db, "user_B")
    assert client.delete("/me", headers=auth(make_token("user_A"))).status_code == 204
    assert identity.deleted == ["user_A"]
    # Table par table : plus aucune ligne pour A ; B est intact.
    for table in Base.metadata.sorted_tables:
        if "user_id" not in table.c:
            continue
        a = db.execute(select(func.count()).select_from(table).where(table.c.user_id == "user_A"))
        b = db.execute(select(func.count()).select_from(table).where(table.c.user_id == "user_B"))
        assert a.scalar_one() == 0, f"{table.name}: rows left for deleted user"
        assert b.scalar_one() > 0, f"{table.name}: other user's rows were removed"


def test_delete_is_idempotent(client: TestClient, make_token: MakeToken) -> None:
    token = make_token("user_A")
    assert client.delete("/me", headers=auth(token)).status_code == 204
    assert client.delete("/me", headers=auth(token)).status_code == 204


def test_delete_still_erases_data_if_identity_provider_is_down(
    client: TestClient, make_token: MakeToken, db: Session, identity: FakeIdentity
) -> None:
    _populate(db, "user_A")
    identity.fail = True
    response = client.delete("/me", headers=auth(make_token("user_A")))
    assert response.status_code == 502
    assert response.json()["code"] == "identity_deletion_failed"
    db.expire_all()
    assert user_data.get_profile(db, "user_A") is None  # données effacées malgré la panne
    identity.fail = False
    assert client.delete("/me", headers=auth(make_token("user_A"))).status_code == 204
    assert identity.deleted == ["user_A"]


def test_rights_require_authentication(client: TestClient) -> None:
    assert client.get("/me/export").status_code == 401
    assert client.delete("/me").status_code == 401


# --- 18 ans minimum (R13)


def test_adult_confirmation_requires_true(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = auth(make_token("user_A"))
    for body in ({"confirmed": False}, {}, {"confirmed": "no"}):
        assert client.post("/me/adult-confirmation", json=body, headers=headers).status_code == 422
    # Rien n'est consigné pour un refus : aucune ligne n'a été créée.
    assert user_data.get_profile(db, "user_A") is None


def test_adult_confirmation_is_logged_once(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = auth(make_token("user_A"))
    assert (
        client.post("/me/adult-confirmation", json={"confirmed": True}, headers=headers).status_code
        == 200
    )
    first = user_data.get_profile(db, "user_A").adult_confirmed_at  # type: ignore[union-attr]
    assert first is not None
    client.post("/me/adult-confirmation", json={"confirmed": True}, headers=headers)
    db.expire_all()
    assert user_data.get_profile(db, "user_A").adult_confirmed_at == first  # type: ignore[union-attr]
    me = client.get("/me", headers=headers).json()
    assert me["adult_confirmed"] is True and me["ai_assist_consent"] is False


def test_require_adult_blocks_until_confirmed(
    app: FastAPI, client: TestClient, make_token: MakeToken, db: Session
) -> None:
    @app.get("/_test/protected")
    def protected(user: CurrentUser = Depends(require_adult)) -> dict[str, str]:
        return {"user": user.user_id}

    headers = auth(make_token("user_A"))
    user_data.ensure_profile(db, "user_A")  # profil créé par le webhook, case non cochée
    db.commit()
    blocked = client.get("/_test/protected", headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["code"] == "adult_confirmation_required"
    client.post("/me/adult-confirmation", json={"confirmed": True}, headers=headers)
    assert client.get("/_test/protected", headers=headers).status_code == 200


def test_get_me_404_without_profile(client: TestClient, make_token: MakeToken) -> None:
    assert client.get("/me", headers=auth(make_token("user_none"))).status_code == 404


def test_truncate_helper_sanity(db: Session) -> None:
    assert db.execute(text("select count(*) from user_profile")).scalar_one() == 0

"""Questionnaire : validation côté serveur, isolation, droits."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.domain.schemas import PreferencesIn
from app.services import preferences as prefs_service
from tests.conftest import auth

MakeToken = Callable[..., str]

VALID: dict[str, Any] = {
    "contract_type": "alternance",
    "duration_months": 12,
    "target_role": "Chargé de marketing digital",
    "sectors": ["marketing_publicite", "informatique_telecoms"],
    "zone": {"location": "69", "radius_km": 50},
    "company_size": ["10-49", "50-249"],
    "priorities": ["sector", "distance"],
    "excluded_sirens": ["552100554"],
}


def _adult(client: TestClient, token: str) -> dict[str, str]:
    headers = auth(token)
    assert client.post(
        "/me/adult-confirmation", json={"confirmed": True}, headers=headers
    ).is_success
    return headers


def test_requires_authentication_and_adult_confirmation(
    client: TestClient, make_token: MakeToken
) -> None:
    assert client.get("/me/preferences").status_code == 401
    assert client.put("/me/preferences", json=VALID).status_code == 401
    headers = auth(make_token("user_A"))  # connecté mais 18+ non confirmé
    blocked = client.put("/me/preferences", json=VALID, headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["code"] == "adult_confirmation_required"


def test_get_is_404_before_first_save(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    assert client.get("/me/preferences", headers=headers).status_code == 404


def test_save_read_and_modify(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    saved = client.put("/me/preferences", json=VALID, headers=headers)
    assert saved.status_code == 200
    body = client.get("/me/preferences", headers=headers).json()
    for key, value in VALID.items():
        assert body[key] == value
    assert "updated_at" in body

    changed = {**VALID, "contract_type": "stage", "duration_months": 4, "priorities": []}
    assert client.put("/me/preferences", json=changed, headers=headers).status_code == 200
    again = client.get("/me/preferences", headers=headers).json()
    assert again["contract_type"] == "stage" and again["priorities"] == []


def test_values_are_normalized(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    payload = {
        **VALID,
        "zone": {"location": " 2a ", "radius_km": 0},
        "excluded_sirens": ["552 100 554"],
        "target_role": "  Data analyst ",
    }
    assert client.put("/me/preferences", json=payload, headers=headers).status_code == 200
    body = client.get("/me/preferences", headers=headers).json()
    assert body["zone"]["location"] == "2A"
    assert body["excluded_sirens"] == ["552100554"]
    assert body["target_role"] == "Data analyst"


def _with(**changes: Any) -> dict[str, Any]:
    payload = deepcopy(VALID)
    payload.update(changes)
    return payload


INVALID_PAYLOADS = {
    "bad contract": _with(contract_type="cdi"),
    "duration 0": _with(duration_months=0),
    "duration 37": _with(duration_months=37),
    "duration text": _with(duration_months="six"),
    "role empty": _with(target_role=" "),
    "role too long": _with(target_role="x" * 101),
    "role html": _with(target_role="<script>alert(1)</script>"),
    "no sector": _with(sectors=[]),
    "unknown sector": _with(sectors=["licornes"]),
    "duplicate sector": _with(sectors=["marketing_publicite", "marketing_publicite"]),
    "too many sectors": _with(sectors=[f"s{i}" for i in range(11)]),
    "bad postcode": _with(zone={"location": "7501", "radius_km": 10}),
    "street address": _with(zone={"location": "12 rue de la Paix", "radius_km": 10}),
    "bad department": _with(zone={"location": "96", "radius_km": 10}),
    "radius negative": _with(zone={"location": "75", "radius_km": -1}),
    "radius too big": _with(zone={"location": "75", "radius_km": 201}),
    "no size": _with(company_size=[]),
    "bad size": _with(company_size=["géante"]),
    "bad priority": _with(priorities=["salary"]),
    "duplicate priority": _with(priorities=["sector", "sector"]),
    "too many priorities": _with(priorities=["sector", "distance", "company_size", "sector"]),
    "bad siren": _with(excluded_sirens=["12345"]),
    "siren letters": _with(excluded_sirens=["55210055A"]),
    "duplicate siren": _with(excluded_sirens=["552100554", "552 100 554"]),
    "too many sirens": _with(excluded_sirens=[f"{i:09d}" for i in range(201)]),
    "forbidden field": {**VALID, "birth_date": "2003-01-01"},
    "user_id injection": {**VALID, "user_id": "user_B"},
}


@pytest.mark.parametrize("name", list(INVALID_PAYLOADS))
def test_invalid_payloads_are_rejected_and_not_saved(
    client: TestClient, make_token: MakeToken, db: Session, name: str
) -> None:
    headers = _adult(client, make_token("user_A"))
    response = client.put("/me/preferences", json=INVALID_PAYLOADS[name], headers=headers)
    assert response.status_code == 422, name
    assert set(response.json()) == {"code", "message"}
    assert prefs_service.get_preferences(db, "user_A") is None


def test_missing_fields_are_rejected(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    assert client.put("/me/preferences", json={}, headers=headers).status_code == 422


def test_unknown_sector_has_a_specific_code(client: TestClient, make_token: MakeToken) -> None:
    headers = _adult(client, make_token("user_A"))
    response = client.put("/me/preferences", json=_with(sectors=["licornes"]), headers=headers)
    assert response.json()["code"] == "unknown_sector"


def test_users_never_see_each_others_preferences(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    a = _adult(client, make_token("user_A"))
    b = _adult(client, make_token("user_B"))
    client.put("/me/preferences", json=VALID, headers=a)
    assert client.get("/me/preferences", headers=b).status_code == 404
    client.put("/me/preferences", json=_with(target_role="Auditeur junior"), headers=b)
    assert client.get("/me/preferences", headers=a).json()["target_role"] == VALID["target_role"]
    row_a = prefs_service.get_preferences(db, "user_A")
    row_b = prefs_service.get_preferences(db, "user_B")
    assert row_a is not None and row_b is not None
    assert row_a.target_role != row_b.target_role
    export = client.get("/me/export", headers=a).json()
    assert "Auditeur junior" not in str(export)


def test_preferences_are_removed_with_the_account(
    client: TestClient, make_token: MakeToken, db: Session
) -> None:
    headers = _adult(client, make_token("user_A"))
    client.put("/me/preferences", json=VALID, headers=headers)
    assert client.delete("/me", headers=headers).status_code == 204
    db.expire_all()
    assert prefs_service.get_preferences(db, "user_A") is None


def test_schema_model_directly() -> None:
    assert PreferencesIn.model_validate(VALID).zone.location == "69"
    with pytest.raises(ValidationError):
        PreferencesIn.model_validate({**VALID, "photo": "x.png"})

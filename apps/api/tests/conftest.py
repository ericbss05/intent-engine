"""Fixtures partagées : base PostgreSQL jetable, faux Clerk (jetons JWT factices), faux fournisseur.

Aucun test ne contacte Clerk ni une vraie base : la base de test est un PostgreSQL local
(Docker en local, service dans la CI) dont le nom DOIT finir par « _test ».
"""

import os
import time
from collections.abc import Callable, Iterator
from typing import Any

# Doit précéder tout import de l'application : fixe un environnement de test hermétique.
# (Les vraies valeurs éventuelles sont gardées pour les tests « integration ».)
REAL_CLERK_JWT_ISSUER = os.environ.get("CLERK_JWT_ISSUER")
os.environ["APP_ENV"] = "test"
for _name in (
    "DATABASE_URL",
    "DATABASE_URL_DIRECT",
    "CLERK_JWT_ISSUER",
    "CLERK_WEBHOOK_SECRET",
    "CLERK_SECRET_KEY",
):
    os.environ.pop(_name, None)

import base64  # noqa: E402

import jwt  # noqa: E402
import pytest  # noqa: E402
from alembic.config import Config  # noqa: E402
from cryptography.hazmat.primitives.asymmetric import rsa  # noqa: E402
from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import Engine, create_engine, text  # noqa: E402
from sqlalchemy.orm import Session, sessionmaker  # noqa: E402

from alembic import command  # noqa: E402
from app.core.config import Settings  # noqa: E402
from app.core.db import get_db, normalize_url  # noqa: E402
from app.core.security import TokenVerifier  # noqa: E402
from app.core.webhook import sign  # noqa: E402
from app.domain.models import Base  # noqa: E402
from app.interfaces.identity import IdentityError  # noqa: E402
from app.main import create_app  # noqa: E402

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/stagefinder_test"
)
ISSUER = "https://test-instance.clerk.accounts.dev"
ORIGIN = "http://localhost:3000"
# Faux secret de webhook (format Svix : « whsec_ » + base64). Pas un vrai secret.
WEBHOOK_SECRET = "whsec_" + base64.b64encode(b"unit-test-webhook-secret-32bytes!").decode()


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = normalize_url(TEST_DATABASE_URL)
    db_name = url.rsplit("/", 1)[-1].split("?")[0]
    # Garde-fou : les tests vident les tables. Jamais sur une autre base qu'une base « _test ».
    if not db_name.endswith("_test"):
        pytest.fail(f"Refusing to run tests on database '{db_name}': name must end with _test")
    eng = create_engine(url)
    try:
        with eng.connect() as conn:
            conn.execute(text("select 1"))
    except Exception as exc:  # pragma: no cover
        pytest.fail(
            "Test PostgreSQL not reachable. Locally: docker run -d -e POSTGRES_PASSWORD=postgres "
            "-e POSTGRES_DB=stagefinder_test -p 5433:5432 postgres:16-alpine "
            f"({type(exc).__name__})"
        )
    # On part d'une base vide et on applique les VRAIES migrations (elles sont donc testées).
    with eng.begin() as conn:
        conn.execute(text("drop schema public cascade"))
        conn.execute(text("create schema public"))
    run_alembic("upgrade", "head")
    yield eng
    eng.dispose()


def run_alembic(action: str, revision: str) -> None:
    os.environ["ALEMBIC_DATABASE_URL"] = TEST_DATABASE_URL
    cfg = Config(os.path.join(os.path.dirname(__file__), "..", "alembic.ini"))
    cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "..", "alembic"))
    getattr(command, action)(cfg, revision)


@pytest.fixture()
def db(engine: Engine) -> Iterator[Session]:
    """Session de test ; les tables sont vidées après chaque test."""
    factory = sessionmaker(engine, expire_on_commit=False)
    with factory() as session:
        yield session
        session.rollback()
    with engine.begin() as conn:
        names = ", ".join(t.name for t in Base.metadata.sorted_tables)
        conn.execute(text(f"truncate {names} restart identity cascade"))


class StaticKeyProvider:
    def __init__(self, key: Any) -> None:
        self._key = key

    def get_key(self, token: str) -> Any:
        return self._key


class FakeIdentity:
    def __init__(self) -> None:
        self.deleted: list[str] = []
        self.fail = False

    def delete_user(self, user_id: str) -> None:
        if self.fail:
            raise IdentityError("simulated outage")
        self.deleted.append(user_id)


@pytest.fixture(scope="session")
def private_key() -> rsa.RSAPrivateKey:
    return rsa.generate_private_key(public_exponent=65537, key_size=2048)


@pytest.fixture()
def make_token(private_key: rsa.RSAPrivateKey) -> Callable[..., str]:
    def _make(
        user_id: str = "user_A",
        role: str | None = None,
        *,
        key: Any = None,
        algorithm: str = "RS256",
        **claim_overrides: Any,
    ) -> str:
        now = int(time.time())
        claims: dict[str, Any] = {
            "sub": user_id,
            "iss": ISSUER,
            "iat": now,
            "nbf": now,
            "exp": now + 60,
            "azp": ORIGIN,
        }
        if role is not None:
            claims["metadata"] = {"role": role}
        claims.update(claim_overrides)
        claims = {k: v for k, v in claims.items() if v is not None}
        return jwt.encode(claims, key or private_key, algorithm=algorithm)

    return _make


@pytest.fixture()
def identity() -> FakeIdentity:
    return FakeIdentity()


@pytest.fixture()
def app(
    engine: Engine, db: Session, private_key: rsa.RSAPrivateKey, identity: FakeIdentity
) -> FastAPI:
    application = create_app(Settings(app_env="test", _env_file=None))
    application.state.token_verifier = TokenVerifier(
        ISSUER, [ORIGIN], StaticKeyProvider(private_key.public_key())
    )
    application.state.identity_provider = identity
    application.state.clerk_webhook_secret = WEBHOOK_SECRET
    factory = sessionmaker(engine, expire_on_commit=False)

    def _get_db() -> Iterator[Session]:
        with factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    application.dependency_overrides[get_db] = _get_db
    return application


@pytest.fixture()
def client(app: FastAPI) -> TestClient:
    return TestClient(app)


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def webhook_headers(body: bytes, *, msg_id: str = "msg_1", ts: int | None = None) -> dict[str, str]:
    timestamp = str(ts if ts is not None else int(time.time()))
    signature = sign(WEBHOOK_SECRET, msg_id, timestamp, body)
    return {
        "svix-id": msg_id,
        "svix-timestamp": timestamp,
        "svix-signature": f"v1,{signature}",
        "content-type": "application/json",
    }

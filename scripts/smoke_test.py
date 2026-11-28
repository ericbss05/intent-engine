#!/usr/bin/env python3
"""Test de fumée avec TES vraies clés (Clerk, Neon). À lancer par toi, jamais en CI.

    cd apps/api
    uv run python ../../scripts/smoke_test.py            # contrôles sans effet de bord
    SMOKE_API_URL=http://localhost:8000 uv run python ../../scripts/smoke_test.py   # + webhook

Variables lues (dans apps/api/.env ou l'environnement ; voir .env.example) :
  DATABASE_URL, CLERK_JWT_ISSUER, CLERK_WEBHOOK_SECRET, CLERK_SECRET_KEY
Variables optionnelles du script :
  SMOKE_API_URL        URL d'un backend déjà lancé (uvicorn) : teste le webhook signé de bout en bout
  SMOKE_SESSION_TOKEN  un jeton de session Clerk copié du navigateur : teste GET /me et /admin/status

Le script n'affiche JAMAIS de secret ni de donnée personnelle (seulement OK / ÉCHEC).
"""

import json
import sys
import time
import urllib.error
import urllib.request

import jwt
from sqlalchemy import create_engine, text

from app.core.config import Settings
from app.core.db import normalize_url
from app.core.webhook import sign

results: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((name, ok, detail))
    print(f"[{'OK' if ok else 'ÉCHEC'}] {name}" + (f" — {detail}" if detail else ""))


def http(method: str, url: str, headers: dict[str, str] | None = None, body: bytes | None = None):
    request = urllib.request.Request(url, method=method, headers=headers or {}, data=body)  # noqa: S310
    try:
        with urllib.request.urlopen(request, timeout=15) as response:  # noqa: S310
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()


def main() -> int:
    try:
        settings = Settings(app_env="production")
        check("Variables d'environnement complètes", True)
    except Exception as exc:
        check("Variables d'environnement complètes", False, str(exc)[:300])
        return 1

    # 1) Base de données (Neon) : connexion + migrations appliquées
    try:
        assert settings.database_url is not None
        url = settings.database_url_direct or settings.database_url
        engine = create_engine(normalize_url(url.get_secret_value()))
        with engine.connect() as conn:
            conn.execute(text("select 1"))
            tables = {
                r[0]
                for r in conn.execute(
                    text("select table_name from information_schema.tables where table_schema='public'")
                )
            }
            version = conn.execute(text("select version_num from alembic_version")).scalar()
        check("Connexion à PostgreSQL", True)
        check("Migrations appliquées (alembic upgrade head)", {"user_profile", "consents"} <= tables, f"version={version}")
    except Exception as exc:
        check("Connexion à PostgreSQL / migrations", False, type(exc).__name__)

    # 2) Clerk : clés publiques de l'émetteur (JWKS)
    try:
        assert settings.clerk_jwt_issuer
        keys = jwt.PyJWKClient(f"{settings.clerk_jwt_issuer}/.well-known/jwks.json", timeout=10).get_signing_keys()
        check("Clerk : JWKS récupéré", len(keys) > 0, f"{len(keys)} clé(s)")
    except Exception as exc:
        check("Clerk : JWKS récupéré", False, type(exc).__name__)

    # 3) Clerk : clé secrète valide (lecture seule, 1 utilisateur, rien n'est affiché)
    assert settings.clerk_secret_key is not None
    status, _ = http(
        "GET",
        "https://api.clerk.com/v1/users?limit=1",
        {"Authorization": f"Bearer {settings.clerk_secret_key.get_secret_value()}"},
    )
    check("Clerk : clé secrète acceptée par l'API Backend", status == 200, f"HTTP {status}")

    # 4) Backend lancé : webhook signé (création puis suppression d'un faux utilisateur)
    api = __import__("os").environ.get("SMOKE_API_URL")
    if api:
        assert settings.clerk_webhook_secret is not None
        secret = settings.clerk_webhook_secret.get_secret_value()
        for event in ("user.created", "user.deleted"):
            body = json.dumps({"type": event, "data": {"id": "user_smoke_test"}}).encode()
            ts = str(int(time.time()))
            sig = sign(secret, f"smoke_{event}", ts, body)
            status, _ = http(
                "POST",
                f"{api.rstrip('/')}/webhooks/clerk",
                {
                    "svix-id": f"smoke_{event}",
                    "svix-timestamp": ts,
                    "svix-signature": f"v1,{sig}",
                    "content-type": "application/json",
                },
                body,
            )
            check(f"Webhook signé « {event} » accepté par le backend", status == 200, f"HTTP {status}")
        status, _ = http("POST", f"{api.rstrip('/')}/webhooks/clerk", {"content-type": "application/json"}, b"{}")
        check("Webhook sans signature refusé", status == 400, f"HTTP {status}")

        token = __import__("os").environ.get("SMOKE_SESSION_TOKEN")
        if token:
            auth = {"Authorization": f"Bearer {token}"}
            status, _ = http("GET", f"{api.rstrip('/')}/me", auth)
            check("Jeton de session réel accepté (GET /me)", status in (200, 404), f"HTTP {status} (404 = pas encore de profil)")
            status, _ = http("GET", f"{api.rstrip('/')}/admin/status", auth)
            check("Rôle admin (GET /admin/status)", status in (200, 403), f"HTTP {status} (200 = admin, 403 = non admin)")
    else:
        print("(SMOKE_API_URL absent : test du webhook et des routes ignoré)")

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} contrôles OK")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

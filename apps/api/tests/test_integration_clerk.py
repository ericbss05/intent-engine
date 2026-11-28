"""Tests qui exigent une VRAIE instance Clerk : ignorés si CLERK_JWT_ISSUER est absent.

Lancer avec : CLERK_JWT_ISSUER=https://<instance>.clerk.accounts.dev uv run pytest -m integration
"""

import pytest

from tests.conftest import REAL_CLERK_JWT_ISSUER

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not REAL_CLERK_JWT_ISSUER, reason="CLERK_JWT_ISSUER not set"),
]


def test_real_jwks_endpoint_publishes_rsa_keys() -> None:
    import jwt

    assert REAL_CLERK_JWT_ISSUER is not None
    client = jwt.PyJWKClient(
        f"{REAL_CLERK_JWT_ISSUER.rstrip('/')}/.well-known/jwks.json", timeout=10
    )
    keys = client.get_signing_keys()
    assert keys and all(k.key_type == "RSA" for k in keys)

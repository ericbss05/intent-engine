"""Authentification : vérification du jeton de session Clerk, côté serveur, à chaque requête.

Principe : le front obtient de Clerk un jeton JWT signé (RS256) et l'envoie dans
`Authorization: Bearer …`. Le backend ne fait confiance à RIEN d'autre : il vérifie la
signature avec les clés PUBLIQUES de Clerk (JWKS), l'émetteur et l'expiration.
L'identité (`user_id`) vient toujours du jeton, jamais d'un paramètre de la requête.
"""

from dataclasses import dataclass
from typing import Any, Protocol

import jwt
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ApiError

# Un seul algorithme accepté : empêche les attaques par « changement d'algorithme ».
_ALGORITHMS = ["RS256"]
_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    user_id: str
    role: str | None = None

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class SigningKeyProvider(Protocol):
    def get_key(self, token: str) -> Any: ...


class JwksKeyProvider:
    """Récupère (et met en cache) les clés publiques publiées par Clerk."""

    def __init__(self, issuer: str) -> None:
        self._client = jwt.PyJWKClient(
            f"{issuer}/.well-known/jwks.json", cache_keys=True, lifespan=3600, timeout=5
        )

    def get_key(self, token: str) -> Any:
        try:
            return self._client.get_signing_key_from_jwt(token).key
        except jwt.PyJWKClientConnectionError as exc:
            # Clerk injoignable : ce n'est pas la faute de l'utilisateur -> 503, pas 401.
            raise ApiError(503, "auth_unavailable", "Authentication service unavailable") from exc
        except jwt.PyJWTError as exc:
            raise ApiError(401, "invalid_token", "Invalid or expired token") from exc


class TokenVerifier:
    def __init__(
        self, issuer: str, authorized_parties: list[str], key_provider: SigningKeyProvider
    ) -> None:
        self._issuer = issuer
        self._authorized_parties = set(authorized_parties)
        self._keys = key_provider

    def verify(self, token: str) -> CurrentUser:
        key = self._keys.get_key(token)
        try:
            claims = jwt.decode(
                token,
                key,
                algorithms=_ALGORITHMS,
                issuer=self._issuer,
                # Les jetons de session Clerk n'ont pas d'« aud » par défaut.
                options={"require": ["exp", "iat", "sub", "iss"], "verify_aud": False},
                leeway=5,
            )
        except jwt.PyJWTError as exc:
            raise ApiError(401, "invalid_token", "Invalid or expired token") from exc

        # « azp » = origine du front qui a obtenu le jeton (recommandation Clerk).
        azp = claims.get("azp")
        if azp is not None and azp not in self._authorized_parties:
            raise ApiError(401, "invalid_token", "Invalid or expired token")

        sub = claims["sub"]
        if not isinstance(sub, str) or not sub:
            raise ApiError(401, "invalid_token", "Invalid or expired token")
        return CurrentUser(user_id=sub, role=_extract_role(claims))


def _extract_role(claims: dict[str, Any]) -> str | None:
    # Le rôle est dans les « public metadata » Clerk (modifiables seulement depuis le
    # tableau de bord ou l'API secrète, pas par l'utilisateur), exposés dans le jeton via
    # un « session token claim » personnalisé : {"metadata": "{{user.public_metadata}}"}.
    metadata = claims.get("metadata")
    if isinstance(metadata, dict):
        role = metadata.get("role")
        if isinstance(role, str):
            return role
    return None


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    verifier: TokenVerifier | None = getattr(request.app.state, "token_verifier", None)
    if verifier is None:
        raise ApiError(503, "auth_unavailable", "Authentication is not configured")
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise ApiError(401, "missing_token", "Authentication required")
    return verifier.verify(credentials.credentials)


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Rôle admin vérifié côté serveur (CLAUDE.md §7), jamais seulement côté front."""
    if not user.is_admin:
        raise ApiError(403, "forbidden", "Admin role required")
    return user

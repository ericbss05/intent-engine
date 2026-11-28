"""Appel à l'API Backend de Clerk : suppression du compte (DELETE /v1/users/{id}).

À vérifier avec une vraie clé (scripts/smoke_test.py) : le chemin et le code 404 « déjà
supprimé » viennent de la documentation Clerk, pas d'un appel réel fait ici.
"""

import urllib.error
import urllib.parse
import urllib.request

from app.interfaces.identity import IdentityError

_BASE_URL = "https://api.clerk.com/v1"


class ClerkIdentityProvider:
    def __init__(self, secret_key: str, timeout_seconds: float = 10.0) -> None:
        self._secret_key = secret_key
        self._timeout = timeout_seconds

    def delete_user(self, user_id: str) -> None:
        url = f"{_BASE_URL}/users/{urllib.parse.quote(user_id, safe='')}"
        request = urllib.request.Request(  # noqa: S310 (URL https fixe, schéma contrôlé)
            url, method="DELETE", headers={"Authorization": f"Bearer {self._secret_key}"}
        )
        try:
            with urllib.request.urlopen(request, timeout=self._timeout):  # noqa: S310
                return
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return  # déjà supprimé : l'opération est idempotente
            # Aucun détail de la réponse dans le message (pourrait contenir des données).
            raise IdentityError(f"Clerk returned HTTP {exc.code}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise IdentityError("Clerk unreachable") from exc

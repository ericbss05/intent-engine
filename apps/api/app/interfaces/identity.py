from typing import Protocol


class IdentityProvider(Protocol):
    """Service qui détient les comptes (Clerk). Remplaçable par un faux dans les tests."""

    def delete_user(self, user_id: str) -> None:
        """Supprime le compte chez le fournisseur. Idempotent. Lève IdentityError si échec."""
        ...


class IdentityError(Exception):
    pass

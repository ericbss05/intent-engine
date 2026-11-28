"""Configuration lue dans les variables d'environnement et validée au démarrage.

Si une valeur est invalide, l'application refuse de démarrer (erreur claire)
plutôt que de planter plus tard de façon obscure. Aucun secret n'est écrit ici.
"""

from functools import lru_cache
from typing import Literal

from pydantic import SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": le .env partagé contient aussi des variables du front.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    # Liste d'origines séparées par des virgules (ex: https://mon-site.vercel.app).
    # Jamais "*" : seul notre front a le droit d'appeler l'API depuis un navigateur.
    api_allowed_origins: str = "http://localhost:3000"

    # --- Base de données (Neon, Frankfurt). Voir .env.example pour pooled vs direct.
    database_url: SecretStr | None = None
    # Connexion directe (sans pooler), utilisée seulement par Alembic (migrations).
    database_url_direct: SecretStr | None = None

    # --- Clerk
    # Émetteur (« iss ») des jetons : l'URL de l'instance Clerk, ex. https://xxx.clerk.accounts.dev
    clerk_jwt_issuer: str | None = None
    # Secret de signature des webhooks (commence par « whsec_ »).
    clerk_webhook_secret: SecretStr | None = None
    # Clé secrète de l'API Clerk : sert uniquement à supprimer le compte Clerk (DELETE /me).
    clerk_secret_key: SecretStr | None = None

    @field_validator("api_allowed_origins")
    @classmethod
    def _no_wildcard(cls, value: str) -> str:
        origins = [o.strip() for o in value.split(",") if o.strip()]
        if not origins or "*" in origins:
            raise ValueError("API_ALLOWED_ORIGINS must list explicit origins, never '*'")
        return ",".join(origins)

    @field_validator("clerk_jwt_issuer")
    @classmethod
    def _issuer_is_https_url(cls, value: str | None) -> str | None:
        if value is None or value == "":
            return None
        value = value.rstrip("/")
        # Le jeton est vérifié avec les clés publiées par l'émetteur : exiger HTTPS
        # évite qu'une faute de configuration fasse confiance à un serveur en clair.
        if not value.startswith("https://"):
            raise ValueError("CLERK_JWT_ISSUER must be an https:// URL")
        return value

    @model_validator(mode="after")
    def _required_outside_tests(self) -> "Settings":
        # En test, les dépendances sont simulées (jeton factice, base jetable) : pas de clé requise.
        if self.app_env == "test":
            return self
        missing = [
            name
            for name, value in (
                ("DATABASE_URL", self.database_url),
                ("CLERK_JWT_ISSUER", self.clerk_jwt_issuer),
                ("CLERK_WEBHOOK_SECRET", self.clerk_webhook_secret),
                ("CLERK_SECRET_KEY", self.clerk_secret_key),
            )
            if value is None or (isinstance(value, SecretStr) and not value.get_secret_value())
        ]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        return self.api_allowed_origins.split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""Configuration lue dans les variables d'environnement et validée au démarrage.

Si une valeur est invalide, l'application refuse de démarrer (erreur claire)
plutôt que de planter plus tard de façon obscure. Aucun secret n'est écrit ici.
"""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": le .env partagé contient aussi des variables du front.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: Literal["development", "test", "production"] = "development"
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    # Liste d'origines séparées par des virgules (ex: https://mon-site.vercel.app).
    # Jamais "*" : seul notre front a le droit d'appeler l'API depuis un navigateur.
    api_allowed_origins: str = "http://localhost:3000"

    @field_validator("api_allowed_origins")
    @classmethod
    def _no_wildcard(cls, value: str) -> str:
        origins = [o.strip() for o in value.split(",") if o.strip()]
        if not origins or "*" in origins:
            raise ValueError("API_ALLOWED_ORIGINS must list explicit origins, never '*'")
        return ",".join(origins)

    @property
    def allowed_origins(self) -> list[str]:
        return self.api_allowed_origins.split(",")


@lru_cache
def get_settings() -> Settings:
    return Settings()

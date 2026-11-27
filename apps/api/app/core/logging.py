"""Logging structuré (une ligne JSON par événement) SANS donnée personnelle.

Règle CLAUDE.md §6.5 : pas d'email, de nom, de texte de CV ni de prompt dans les logs.
On n'enregistre donc que des champs techniques fixes (méthode, chemin, statut, durée).
Le filtre ci-dessous est une seconde barrière : il retire les champs interdits
si quelqu'un en ajoute par erreur via `extra=`.
"""

import json
import logging
from datetime import UTC, datetime

# Champs techniques autorisés dans les logs (liste blanche, plus sûre qu'une liste noire).
ALLOWED_EXTRA_FIELDS = frozenset({"method", "path", "status_code", "duration_ms", "event"})

_STANDARD_ATTRS = frozenset(vars(logging.makeLogRecord({}))) | {"message", "asctime"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),  # UTC (CLAUDE.md §5)
            "level": record.levelname.lower(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in vars(record).items():
            if key not in _STANDARD_ATTRS and key in ALLOWED_EXTRA_FIELDS:
                payload[key] = value
        if record.exc_info:
            # Seulement le type d'exception : le message pourrait contenir une donnée personnelle.
            exc_type = record.exc_info[0]
            payload["exception"] = exc_type.__name__ if exc_type else "unknown"
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    # Uvicorn logge l'URL complète (avec query string) : on coupe son log d'accès
    # et on utilise notre propre middleware qui ne garde que le chemin.
    logging.getLogger("uvicorn.access").disabled = True

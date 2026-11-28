import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.adapters.clerk import ClerkIdentityProvider
from app.core.config import Settings, get_settings
from app.core.db import init_db
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.core.security import JwksKeyProvider, TokenVerifier
from app.domain.reference import load_reference_data
from app.routers import admin, consents, health, me, preferences, reference, webhooks

logger = logging.getLogger("app.request")


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)
    init_db(settings)

    # Pas de documentation interactive publique en production.
    docs_enabled = settings.app_env != "production"
    app = FastAPI(
        title="stage-finder API",
        docs_url="/docs" if docs_enabled else None,
        redoc_url=None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    # CORS : le navigateur n'autorise le front à lire nos réponses que depuis
    # les origines listées. Les en-têtes autorisés sont restreints au strict nécessaire.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        logger.info(
            "request",
            extra={
                "method": request.method,
                "path": request.url.path,  # sans query string (pourrait contenir des données)
                "status_code": response.status_code,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
            },
        )
        return response

    register_error_handlers(app)

    # Données de référence validées au démarrage (échec = l'application ne démarre pas).
    app.state.reference = load_reference_data(settings.resolved_data_dir)

    # Services externes, accrochés à l'application (remplaçables par des faux dans les tests).
    if settings.clerk_jwt_issuer:
        app.state.token_verifier = TokenVerifier(
            issuer=settings.clerk_jwt_issuer,
            authorized_parties=settings.allowed_origins,
            key_provider=JwksKeyProvider(settings.clerk_jwt_issuer),
        )
    if settings.clerk_webhook_secret:
        app.state.clerk_webhook_secret = settings.clerk_webhook_secret.get_secret_value()
    if settings.clerk_secret_key:
        app.state.identity_provider = ClerkIdentityProvider(
            settings.clerk_secret_key.get_secret_value()
        )

    app.include_router(health.router)
    app.include_router(me.router)
    app.include_router(admin.router)
    app.include_router(preferences.router)
    app.include_router(consents.router)
    app.include_router(reference.router)
    app.include_router(webhooks.router)
    return app


app = create_app()

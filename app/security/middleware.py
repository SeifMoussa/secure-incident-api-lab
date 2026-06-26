"""Security middleware registration helpers."""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app.audit.middleware import AuditMiddleware
from app.config import Settings
from app.security.cors import allowed_cors_origins
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limit import InMemoryRateLimitMiddleware


def add_security_middleware(app: FastAPI, settings: Settings) -> None:
    """Register security middleware in a deliberate response-safe order."""
    if settings.https_redirect_is_enabled:
        app.add_middleware(HTTPSRedirectMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_cors_origins(settings),
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.add_middleware(InMemoryRateLimitMiddleware, settings=settings)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)

"""FastAPI application factory for the Secure Incident Management API."""

from fastapi import FastAPI

from app.admin.router import router as admin_router
from app.audit.router import router as audit_router
from app.auth.router import router as auth_router
from app.common.error_handlers import add_error_handlers
from app.common.health import build_health_response
from app.config import Settings, get_settings
from app.evidence.router import router as evidence_router
from app.incidents.router import router as incidents_router
from app.remediation.router import router as remediation_router
from app.security.middleware import add_security_middleware
from app.tickets.router import router as tickets_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""
    resolved_settings = settings or get_settings()
    docs_url = "/docs" if resolved_settings.docs_are_enabled else None
    redoc_url = "/redoc" if resolved_settings.docs_are_enabled else None
    openapi_url = "/openapi.json" if resolved_settings.docs_are_enabled else None

    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.version,
        debug=resolved_settings.debug,
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
    )
    app.state.settings = resolved_settings
    add_error_handlers(app)
    add_security_middleware(app, resolved_settings)
    app.include_router(auth_router)
    app.include_router(admin_router)
    app.include_router(audit_router)
    app.include_router(incidents_router)
    app.include_router(tickets_router)
    app.include_router(evidence_router)
    app.include_router(remediation_router)

    @app.get("/", tags=["service"])
    def root() -> dict[str, str]:
        return {
            "service": resolved_settings.app_name,
            "message": "Secure Incident Management API scaffold is running.",
        }

    @app.get("/health", tags=["health"])
    def health() -> dict[str, str | bool]:
        return build_health_response(resolved_settings)

    return app


app = create_app()

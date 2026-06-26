"""Health response helpers."""

from app.config import Settings


def build_health_response(settings: Settings) -> dict[str, str | bool]:
    """Build the Phase 1 health response without external dependency checks."""
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.version,
        "environment": settings.environment,
        "docs_enabled": settings.docs_are_enabled,
    }

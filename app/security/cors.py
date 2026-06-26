"""CORS configuration helpers."""

from app.config import Settings


def allowed_cors_origins(settings: Settings) -> list[str]:
    """Return an explicit CORS allowlist without wildcard origins."""
    return settings.effective_cors_allowed_origins

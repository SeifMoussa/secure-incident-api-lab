"""Security header middleware."""

from collections.abc import Callable
from typing import Any

from app.config import Settings

DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


class SecurityHeadersMiddleware:
    """Apply conservative security headers to HTTP responses."""

    def __init__(self, app: Callable[..., Any], settings: Settings) -> None:
        self.app = app
        self.settings = settings

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def add_headers(message: dict[str, Any]) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                existing = {key.lower() for key, _ in headers}
                for key, value in self._headers_for_path(scope["path"]).items():
                    key_bytes = key.lower().encode("latin1")
                    if key_bytes not in existing:
                        headers.append((key_bytes, value.encode("latin1")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, add_headers)

    def _headers_for_path(self, path: str) -> dict[str, str]:
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "no-referrer",
        }
        if self._should_apply_api_headers(path):
            headers["Cache-Control"] = "no-store"
            headers["Content-Security-Policy"] = "default-src 'none'"
        if self.settings.hsts_is_enabled:
            headers["Strict-Transport-Security"] = (
                f"max-age={self.settings.hsts_max_age_seconds}; includeSubDomains"
            )
        return headers

    def _should_apply_api_headers(self, path: str) -> bool:
        return not (self.settings.docs_are_enabled and path.startswith(DOCS_PATHS))

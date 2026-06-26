"""Local in-memory rate limiting middleware."""

from collections import defaultdict, deque
from collections.abc import Callable
from time import monotonic
from typing import Any

from starlette.responses import JSONResponse

from app.config import Settings


class InMemoryRateLimitMiddleware:
    """Apply simple per-IP fixed-window request limits."""

    def __init__(self, app: Callable[..., Any], settings: Settings) -> None:
        self.app = app
        self.settings = settings
        self._requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if (
            scope["type"] != "http"
            or not self.settings.rate_limit_enabled
            or scope["method"].upper() == "OPTIONS"
        ):
            await self.app(scope, receive, send)
            return

        key = (self._client_host(scope), self._bucket_for_path(scope["path"]))
        limit = self._limit_for_bucket(key[1])
        now = monotonic()
        window_start = now - self.settings.rate_limit_window_seconds
        requests = self._requests[key]
        while requests and requests[0] <= window_start:
            requests.popleft()

        if len(requests) >= limit:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests."},
                headers={"Retry-After": str(self.settings.rate_limit_window_seconds)},
            )
            await response(scope, receive, send)
            return

        requests.append(now)
        await self.app(scope, receive, send)

    def _bucket_for_path(self, path: str) -> str:
        if path == "/auth/login":
            return "auth_login"
        return "default"

    def _limit_for_bucket(self, bucket: str) -> int:
        if bucket == "auth_login":
            return self.settings.rate_limit_login_per_minute
        return self.settings.rate_limit_default_per_minute

    def _client_host(self, scope: dict[str, Any]) -> str:
        client = scope.get("client")
        if client is None:
            return "unknown"
        return str(client[0])

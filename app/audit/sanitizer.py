"""Audit sanitization helpers."""

import re
from collections.abc import Mapping
from typing import Any

REDACTED = "[REDACTED]"

SENSITIVE_KEY_PARTS = (
    "password",
    "password_hash",
    "access_token",
    "refresh_token",
    "authorization",
    "api_key",
    "secret",
    "jwt_secret",
    "bearer",
    "cookie",
    "set-cookie",
)

JWT_SHAPED_VALUE = re.compile(r"^[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}$")
API_KEY_PREFIXES = ("sk-", "pk_", "rk_", "api_")


def is_sensitive_key(key: str) -> bool:
    """Return whether a key name should be treated as sensitive."""
    normalized = key.lower().replace("-", "_")
    return any(part in normalized for part in SENSITIVE_KEY_PARTS)


def sanitize_audit_value(value: Any) -> Any:
    """Recursively sanitize values before they can be written to audit logs."""
    if isinstance(value, Mapping):
        sanitized: dict[str, Any] = {}
        for key, nested_value in value.items():
            key_text = str(key)
            sanitized[key_text] = REDACTED
            if not is_sensitive_key(key_text):
                sanitized[key_text] = sanitize_audit_value(nested_value)
        return sanitized
    if isinstance(value, list | tuple):
        return [sanitize_audit_value(item) for item in value]
    if isinstance(value, str) and _looks_like_secret_value(value):
        return REDACTED
    return value


def safe_field_summary(payload: Any) -> dict[str, object]:
    """Return safe field names from a request body without raw values."""
    if not isinstance(payload, Mapping):
        return {"fields_changed": []}
    fields = sorted(str(key) for key in payload if not is_sensitive_key(str(key)))
    redacted = any(is_sensitive_key(str(key)) for key in payload)
    summary: dict[str, object] = {"fields_changed": fields}
    if redacted:
        summary["redacted_sensitive_fields"] = True
    return summary


def _looks_like_secret_value(value: str) -> bool:
    stripped = value.strip()
    lowered = stripped.lower()
    if lowered.startswith("bearer "):
        return True
    if lowered.startswith(("cookie:", "set-cookie:")):
        return True
    if any(lowered.startswith(prefix) for prefix in API_KEY_PREFIXES):
        return True
    return bool(JWT_SHAPED_VALUE.fullmatch(stripped))

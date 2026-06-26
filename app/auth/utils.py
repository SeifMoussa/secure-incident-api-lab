"""Authentication utility functions for password hashing and JWT handling."""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import Settings

ACCESS_TOKEN_TYPE = "access"  # noqa: S105
REFRESH_TOKEN_TYPE = "refresh"  # noqa: S105
JWT_ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class TokenError(ValueError):
    """Raised when a token is invalid for the requested operation."""


def hash_password(password: str) -> str:
    """Hash a raw password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a raw password against a stored hash."""
    return pwd_context.verify(password, password_hash)


def create_access_token(settings: Settings, *, user_id: str, role: str) -> str:
    """Create a signed access token for an authenticated user."""
    return _create_token(
        settings,
        user_id=user_id,
        role=role,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.access_token_minutes),
    )


def create_refresh_token(settings: Settings, *, user_id: str, role: str) -> str:
    """Create a signed refresh token for an authenticated user."""
    return _create_token(
        settings,
        user_id=user_id,
        role=role,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.refresh_token_days),
    )


def decode_token(
    settings: Settings, token: str, *, expected_type: str | None = None
) -> dict[str, str]:
    """Decode and validate a signed JWT."""
    secret = _require_jwt_secret(settings)
    try:
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        msg = "Invalid token."
        raise TokenError(msg) from exc

    token_type = payload.get("type")
    subject = payload.get("sub")
    jti = payload.get("jti")
    if not isinstance(token_type, str) or not isinstance(subject, str) or not isinstance(jti, str):
        msg = "Invalid token claims."
        raise TokenError(msg)
    if expected_type is not None and token_type != expected_type:
        msg = "Invalid token type."
        raise TokenError(msg)
    return payload


def extract_jti(settings: Settings, token: str, *, expected_type: str | None = None) -> str:
    """Return the JTI from a validated token."""
    return decode_token(settings, token, expected_type=expected_type)["jti"]


def _create_token(
    settings: Settings,
    *,
    user_id: str,
    role: str,
    token_type: str,
    expires_delta: timedelta,
) -> str:
    secret = _require_jwt_secret(settings)
    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "role": role,
        "type": token_type,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def _require_jwt_secret(settings: Settings) -> str:
    if not settings.jwt_secret_key:
        msg = "JWT secret is not configured."
        raise TokenError(msg)
    return settings.jwt_secret_key

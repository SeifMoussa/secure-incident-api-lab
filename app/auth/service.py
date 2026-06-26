"""Authentication service functions."""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.models import TokenBlocklist, User
from app.auth.password_policy import PasswordPolicyError, validate_password_policy
from app.auth.schemas import (
    AccessTokenResponse,
    AuthMessageResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfileResponse,
)
from app.auth.utils import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.common.enums import Role
from app.config import Settings


class AuthServiceError(ValueError):
    """Raised for expected safe authentication failures."""


def register_user(db: Session, payload: RegisterRequest) -> UserProfileResponse:
    """Register a synthetic user and return a safe profile."""
    try:
        validate_password_policy(payload.password)
    except PasswordPolicyError as exc:
        raise AuthServiceError(str(exc)) from exc

    normalized_email = payload.email.lower()
    existing_user = db.scalar(select(User).where(User.email == normalized_email))
    if existing_user is not None:
        msg = "Email is already registered."
        raise AuthServiceError(msg)

    user = User(
        email=normalized_email,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        role=Role.ANALYST,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        msg = "Email is already registered."
        raise AuthServiceError(msg) from exc
    db.refresh(user)
    return user_profile(user)


def login_user(db: Session, settings: Settings, payload: LoginRequest) -> TokenResponse:
    """Authenticate a user and issue access and refresh tokens."""
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if user is None or not verify_password(payload.password, user.password_hash):
        msg = "Invalid email or password."
        raise AuthServiceError(msg)
    if not user.is_active:
        msg = "Invalid email or password."
        raise AuthServiceError(msg)

    access_token = create_access_token(settings, user_id=user.user_id, role=user.role.value)
    refresh_token = create_refresh_token(settings, user_id=user.user_id, role=user.role.value)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


def refresh_access_token(
    db: Session,
    settings: Settings,
    payload: RefreshRequest,
) -> AccessTokenResponse:
    """Validate a refresh token and issue a new access token."""
    token_payload = _decode_refresh_token(settings, payload.refresh_token)
    if is_jti_blocklisted(db, token_payload["jti"]):
        msg = "Invalid refresh token."
        raise AuthServiceError(msg)

    user = db.get(User, token_payload["sub"])
    if user is None or not user.is_active:
        msg = "Invalid refresh token."
        raise AuthServiceError(msg)

    access_token = create_access_token(settings, user_id=user.user_id, role=user.role.value)
    return AccessTokenResponse(access_token=access_token)


def logout_user(db: Session, settings: Settings, refresh_token: str) -> AuthMessageResponse:
    """Blocklist a refresh token JTI without storing the raw token."""
    try:
        token_payload = _decode_refresh_token(settings, refresh_token)
    except AuthServiceError:
        return AuthMessageResponse(message="Logged out.")

    block_refresh_token_jti(
        db,
        jti=token_payload["jti"],
        expires_at=datetime.fromtimestamp(int(token_payload["exp"]), tz=UTC),
    )
    return AuthMessageResponse(message="Logged out.")


def get_user_from_access_token(db: Session, settings: Settings, token: str) -> User:
    """Resolve the current user from an access token."""
    try:
        token_payload = decode_token(settings, token, expected_type=ACCESS_TOKEN_TYPE)
    except TokenError as exc:
        msg = "Invalid authentication credentials."
        raise AuthServiceError(msg) from exc

    user = db.get(User, token_payload["sub"])
    if user is None or not user.is_active:
        msg = "Invalid authentication credentials."
        raise AuthServiceError(msg)
    return user


def block_refresh_token_jti(db: Session, *, jti: str, expires_at: datetime) -> None:
    """Persist a blocked refresh-token JTI idempotently."""
    if is_jti_blocklisted(db, jti):
        return
    db.add(TokenBlocklist(jti=jti, token_type=REFRESH_TOKEN_TYPE, expires_at=expires_at))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()


def is_jti_blocklisted(db: Session, jti: str) -> bool:
    """Return whether a token JTI has been blocklisted."""
    return db.scalar(select(TokenBlocklist).where(TokenBlocklist.jti == jti)) is not None


def user_profile(user: User) -> UserProfileResponse:
    """Convert a user model into a safe profile response."""
    return UserProfileResponse(
        user_id=user.user_id,
        email=user.email,
        display_name=user.display_name,
        role=user.role,
        is_active=user.is_active,
    )


def _decode_refresh_token(settings: Settings, refresh_token: str) -> dict[str, str]:
    try:
        return decode_token(settings, refresh_token, expected_type=REFRESH_TOKEN_TYPE)
    except TokenError as exc:
        msg = "Invalid refresh token."
        raise AuthServiceError(msg) from exc

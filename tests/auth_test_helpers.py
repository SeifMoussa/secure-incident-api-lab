from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth.models import User
from app.auth.utils import create_access_token, create_refresh_token, hash_password
from app.common.enums import Role
from app.config import Settings

TEST_ONLY_PASSWORD = "SyntheticPhase4!123"


def create_synthetic_user(
    db_session: Session,
    *,
    email: str,
    role: Role,
    is_active: bool = True,
    password: str = TEST_ONLY_PASSWORD,
) -> User:
    user = User(
        email=email,
        display_name=f"Synthetic {role.value.title()}",
        password_hash=hash_password(password),
        role=role,
        is_active=is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def bearer_header(settings: Settings, user: User) -> dict[str, str]:
    token = create_access_token(settings, user_id=user.user_id, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


def refresh_bearer_header(settings: Settings, user: User) -> dict[str, str]:
    token = create_refresh_token(settings, user_id=user.user_id, role=user.role.value)
    return {"Authorization": f"Bearer {token}"}


def expired_bearer_header(settings: Settings, user: User) -> dict[str, str]:
    from jose import jwt

    payload = {
        "sub": user.user_id,
        "role": user.role.value,
        "type": "access",
        "jti": "synthetic-expired-jti",
        "iat": datetime.now(UTC) - timedelta(minutes=30),
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")
    return {"Authorization": f"Bearer {token}"}

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.dependencies import require_admin
from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import (
    bearer_header,
    create_synthetic_user,
    expired_bearer_header,
    refresh_bearer_header,
)


def test_require_admin_allows_admin(db_session: Session) -> None:
    admin = create_synthetic_user(db_session, email="rbac-admin@example.com", role=Role.ADMIN)
    dependency = require_admin

    assert dependency(admin) is admin


@pytest.mark.parametrize("role", [Role.ANALYST, Role.VIEWER, Role.AUDITOR])
def test_require_admin_blocks_non_admin_roles(db_session: Session, role: Role) -> None:
    user = create_synthetic_user(
        db_session, email=f"rbac-{role.value.lower()}@example.com", role=role
    )

    with pytest.raises(HTTPException) as exc_info:
        require_admin(user)

    assert exc_info.value.status_code == 403


def test_missing_token_returns_401(client: TestClient) -> None:
    response = client.get("/admin/users/")

    assert response.status_code == 401


def test_invalid_token_returns_401(client: TestClient) -> None:
    response = client.get("/admin/users/", headers={"Authorization": "Bearer invalid.token.value"})

    assert response.status_code == 401


def test_expired_token_returns_401(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="expired-admin@example.com", role=Role.ADMIN)

    response = client.get("/admin/users/", headers=expired_bearer_header(test_settings, admin))

    assert response.status_code == 401


def test_refresh_token_used_as_access_token_returns_401(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="refresh-admin@example.com", role=Role.ADMIN)

    response = client.get("/admin/users/", headers=refresh_bearer_header(test_settings, admin))

    assert response.status_code == 401


def test_inactive_user_with_valid_token_returns_401(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session,
        email="inactive-admin@example.com",
        role=Role.ADMIN,
        is_active=False,
    )

    response = client.get("/admin/users/", headers=bearer_header(test_settings, admin))

    assert response.status_code == 401


def test_authorization_uses_database_role_not_stale_token_claim(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    user = create_synthetic_user(db_session, email="stale-role@example.com", role=Role.ADMIN)
    stale_admin_header = bearer_header(test_settings, user)
    user.role = Role.ANALYST
    db_session.commit()

    response = client.get("/admin/users/", headers=stale_admin_header)

    assert response.status_code == 403

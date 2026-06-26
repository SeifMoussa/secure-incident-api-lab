from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user


def test_admin_can_deactivate_another_user(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="deactivate-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(
        db_session, email="deactivate-target@example.com", role=Role.ANALYST
    )

    response = client.delete(
        f"/admin/users/{target.user_id}",
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 200
    assert response.json()["message"] == "User deactivated."
    assert response.json()["user"]["is_active"] is False
    db_session.refresh(target)
    assert target.is_active is False


def test_non_admin_cannot_deactivate_users(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    analyst = create_synthetic_user(
        db_session,
        email="deactivate-analyst@example.com",
        role=Role.ANALYST,
    )
    target = create_synthetic_user(
        db_session, email="deactivate-viewer@example.com", role=Role.VIEWER
    )

    response = client.delete(
        f"/admin/users/{target.user_id}",
        headers=bearer_header(test_settings, analyst),
    )

    assert response.status_code == 403


def test_admin_self_deactivation_is_blocked(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="self-deactivate-admin@example.com", role=Role.ADMIN
    )

    response = client.delete(
        f"/admin/users/{admin.user_id}",
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Admins cannot deactivate their own account."


def test_deactivated_user_cannot_login(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="login-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(
        db_session,
        email="deactivated-login@example.com",
        role=Role.ANALYST,
    )

    client.delete(f"/admin/users/{target.user_id}", headers=bearer_header(test_settings, admin))
    response = client.post(
        "/auth/login",
        json={"email": "deactivated-login@example.com", "password": TEST_ONLY_PASSWORD},
    )

    assert response.status_code == 401


def test_deactivated_user_cannot_use_existing_access_token(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="token-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(db_session, email="token-target@example.com", role=Role.ANALYST)
    target_header = bearer_header(test_settings, target)

    client.delete(f"/admin/users/{target.user_id}", headers=bearer_header(test_settings, admin))
    response = client.get("/auth/me", headers=target_header)

    assert response.status_code == 401

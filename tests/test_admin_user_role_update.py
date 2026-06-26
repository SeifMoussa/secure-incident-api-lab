from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def test_admin_can_change_another_users_role(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="role-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(db_session, email="role-target@example.com", role=Role.VIEWER)

    response = client.patch(
        f"/admin/users/{target.user_id}/role",
        json={"role": "ANALYST"},
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 200
    assert response.json()["role"] == "ANALYST"
    db_session.refresh(target)
    assert target.role == Role.ANALYST


def test_invalid_role_is_rejected(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="invalid-role-admin@example.com", role=Role.ADMIN
    )
    target = create_synthetic_user(
        db_session, email="invalid-role-target@example.com", role=Role.VIEWER
    )

    response = client.patch(
        f"/admin/users/{target.user_id}/role",
        json={"role": "OWNER"},
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 422


def test_non_admin_cannot_change_role(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    analyst = create_synthetic_user(db_session, email="role-analyst@example.com", role=Role.ANALYST)
    target = create_synthetic_user(db_session, email="role-viewer@example.com", role=Role.VIEWER)

    response = client.patch(
        f"/admin/users/{target.user_id}/role",
        json={"role": "ADMIN"},
        headers=bearer_header(test_settings, analyst),
    )

    assert response.status_code == 403


def test_admin_self_role_change_is_blocked(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="self-role-admin@example.com", role=Role.ADMIN)

    response = client.patch(
        f"/admin/users/{admin.user_id}/role",
        json={"role": "ANALYST"},
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Admins cannot change their own role."

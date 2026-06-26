from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def test_admin_can_list_users(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="list-admin@example.com", role=Role.ADMIN)
    create_synthetic_user(db_session, email="list-analyst@example.com", role=Role.ANALYST)

    response = client.get("/admin/users/", headers=bearer_header(test_settings, admin))

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 20
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert "password_hash" not in response.text
    assert "access_token" not in response.text
    assert "refresh_token" not in response.text


def test_admin_user_list_pagination_defaults_and_page_size_limit(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="pagination-admin@example.com", role=Role.ADMIN)

    default_response = client.get("/admin/users/", headers=bearer_header(test_settings, admin))
    too_large_response = client.get(
        "/admin/users/?page_size=101",
        headers=bearer_header(test_settings, admin),
    )

    assert default_response.status_code == 200
    assert default_response.json()["page"] == 1
    assert default_response.json()["page_size"] == 20
    assert too_large_response.status_code == 422


def test_non_admin_roles_cannot_list_users(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    for role in [Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session,
            email=f"cannot-list-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.get("/admin/users/", headers=bearer_header(test_settings, user))

        assert response.status_code == 403


def test_admin_can_get_user_detail(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="detail-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(db_session, email="detail-target@example.com", role=Role.VIEWER)

    response = client.get(
        f"/admin/users/{target.user_id}",
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "detail-target@example.com"
    assert "password_hash" not in response.text
    assert "token" not in response.text


def test_non_admin_cannot_get_user_detail(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    analyst = create_synthetic_user(
        db_session, email="detail-analyst@example.com", role=Role.ANALYST
    )
    target = create_synthetic_user(
        db_session, email="detail-admin-target@example.com", role=Role.ADMIN
    )

    response = client.get(
        f"/admin/users/{target.user_id}",
        headers=bearer_header(test_settings, analyst),
    )

    assert response.status_code == 403

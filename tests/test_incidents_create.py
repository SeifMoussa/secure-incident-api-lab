from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def valid_payload(**overrides):
    payload = {
        "title": "Synthetic incident title",
        "description": "Synthetic defensive incident data for test-only use.",
        "severity": "HIGH",
        "status": "OPEN",
        "tags": ["Synthetic", "Defensive"],
    }
    payload.update(overrides)
    return payload


def test_admin_can_create_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="incident-admin@example.com", role=Role.ADMIN)

    response = client.post(
        "/incidents/",
        json=valid_payload(),
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["created_by"] == admin.user_id
    assert body["is_deleted"] is False
    assert body["tags"] == ["synthetic", "defensive"]
    assert "password_hash" not in response.text
    assert "token" not in response.text


def test_analyst_can_create_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    analyst = create_synthetic_user(
        db_session,
        email="incident-analyst@example.com",
        role=Role.ANALYST,
    )

    response = client.post(
        "/incidents/",
        json=valid_payload(),
        headers=bearer_header(test_settings, analyst),
    )

    assert response.status_code == 201


def test_viewer_and_auditor_cannot_create_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session,
            email=f"create-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.post(
            "/incidents/",
            json=valid_payload(),
            headers=bearer_header(test_settings, user),
        )

        assert response.status_code == 403


def test_create_rejects_missing_invalid_and_inactive_auth(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    inactive = create_synthetic_user(
        db_session,
        email="inactive-incident@example.com",
        role=Role.ADMIN,
        is_active=False,
    )

    assert client.post("/incidents/", json=valid_payload()).status_code == 401
    assert (
        client.post(
            "/incidents/",
            json=valid_payload(),
            headers={"Authorization": "Bearer invalid.token.value"},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/incidents/",
            json=valid_payload(),
            headers=bearer_header(test_settings, inactive),
        ).status_code
        == 401
    )


def test_client_cannot_override_managed_create_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="managed-admin@example.com", role=Role.ADMIN)
    payload = valid_payload(created_by="client-value", is_deleted=True, created_at="2026-01-01")

    response = client.post(
        "/incidents/",
        json=payload,
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 422


def test_create_assigned_to_must_exist_and_be_active(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="assign-admin@example.com", role=Role.ADMIN)
    inactive = create_synthetic_user(
        db_session,
        email="assign-inactive@example.com",
        role=Role.ANALYST,
        is_active=False,
    )
    active = create_synthetic_user(db_session, email="assign-active@example.com", role=Role.ANALYST)

    inactive_response = client.post(
        "/incidents/",
        json=valid_payload(assigned_to=inactive.user_id),
        headers=bearer_header(test_settings, admin),
    )
    missing_response = client.post(
        "/incidents/",
        json=valid_payload(assigned_to="00000000-0000-0000-0000-000000000000"),
        headers=bearer_header(test_settings, admin),
    )
    active_response = client.post(
        "/incidents/",
        json=valid_payload(assigned_to=active.user_id),
        headers=bearer_header(test_settings, admin),
    )

    assert inactive_response.status_code == 400
    assert missing_response.status_code == 400
    assert active_response.status_code == 201

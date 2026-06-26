from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def ticket_payload(**overrides):
    payload = {
        "title": "Synthetic ticket",
        "description": "Synthetic ticket description for test-only use.",
        "status": "OPEN",
        "priority": "P2",
    }
    payload.update(overrides)
    return payload


def test_admin_and_analyst_can_create_ticket(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    creator = create_synthetic_user(
        db_session, email="ticket-incident-creator@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=creator.user_id)
    for role in [Role.ADMIN, Role.ANALYST]:
        user = create_synthetic_user(
            db_session, email=f"ticket-create-{role.value.lower()}@example.com", role=role
        )
        response = client.post(
            f"/incidents/{incident.incident_id}/tickets/",
            json=ticket_payload(),
            headers=bearer_header(test_settings, user),
        )
        assert response.status_code == 201
        assert response.json()["created_by"] == user.user_id


def test_ticket_create_rejects_read_roles_missing_incident_and_bad_assignee(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="ticket-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    inactive = create_synthetic_user(
        db_session,
        email="ticket-inactive@example.com",
        role=Role.ANALYST,
        is_active=False,
    )
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"ticket-deny-{role.value.lower()}@example.com", role=role
        )
        assert (
            client.post(
                f"/incidents/{incident.incident_id}/tickets/",
                json=ticket_payload(),
                headers=bearer_header(test_settings, user),
            ).status_code
            == 403
        )
    assert (
        client.post(
            "/incidents/missing/tickets/",
            json=ticket_payload(),
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 404
    )
    assert (
        client.post(
            f"/incidents/{incident.incident_id}/tickets/",
            json=ticket_payload(assigned_to=inactive.user_id),
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 404
    )


def test_ticket_create_validation_rejects_bad_payload(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="ticket-validation-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    cases = [
        ticket_payload(title="bad"),
        ticket_payload(description="x" * 2001),
        ticket_payload(status="UNKNOWN"),
        ticket_payload(priority="P0"),
        ticket_payload(created_by=admin.user_id),
    ]
    for payload in cases:
        response = client.post(
            f"/incidents/{incident.incident_id}/tickets/",
            json=payload,
            headers=bearer_header(test_settings, admin),
        )
        assert response.status_code == 422

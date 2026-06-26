from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_tickets_create import ticket_payload


def test_ticket_update_delete_rbac_matrix(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="ticket-matrix-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    for role, expected in {
        Role.ADMIN: 200,
        Role.ANALYST: 200,
        Role.VIEWER: 403,
        Role.AUDITOR: 403,
    }.items():
        ticket = client.post(
            f"/incidents/{incident.incident_id}/tickets/",
            json=ticket_payload(),
            headers=bearer_header(test_settings, admin),
        ).json()
        user = (
            admin
            if role == Role.ADMIN
            else create_synthetic_user(
                db_session,
                email=f"ticket-matrix-{role.value.lower()}@example.com",
                role=role,
            )
        )
        patch_response = client.patch(
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}",
            json={"title": "Updated ticket", "status": "DONE", "priority": "P1"},
            headers=bearer_header(test_settings, user),
        )
        delete_response = client.delete(
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}",
            headers=bearer_header(test_settings, user),
        )
        assert patch_response.status_code == expected
        assert delete_response.status_code == expected

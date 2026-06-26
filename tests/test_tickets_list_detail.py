from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_tickets_create import ticket_payload


def _create_ticket(client: TestClient, settings: Settings, user, incident_id: str) -> dict:
    response = client.post(
        f"/incidents/{incident_id}/tickets/",
        json=ticket_payload(),
        headers=bearer_header(settings, user),
    )
    assert response.status_code == 201
    return response.json()


def test_ticket_list_and_detail_for_all_roles(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="ticket-list-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    ticket = _create_ticket(client, test_settings, admin, incident.incident_id)
    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"ticket-read-{role.value.lower()}@example.com", role=role
        )
        header = bearer_header(test_settings, user)
        list_response = client.get(f"/incidents/{incident.incident_id}/tickets/", headers=header)
        detail_response = client.get(
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}",
            headers=header,
        )
        assert list_response.status_code == 200
        assert list_response.json()["total"] == 1
        assert detail_response.status_code == 200


def test_ticket_detail_scoping_and_soft_delete(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="ticket-scope-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    other = create_synthetic_incident(db_session, created_by=admin.user_id)
    ticket = _create_ticket(client, test_settings, admin, incident.incident_id)
    header = bearer_header(test_settings, admin)
    assert (
        client.get(
            f"/incidents/{other.incident_id}/tickets/{ticket['ticket_id']}", headers=header
        ).status_code
        == 404
    )
    assert (
        client.delete(
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}", headers=header
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}", headers=header
        ).status_code
        == 404
    )
    assert (
        client.get(f"/incidents/{incident.incident_id}/tickets/", headers=header).json()["total"]
        == 0
    )

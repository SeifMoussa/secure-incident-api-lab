from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_incidents_create import valid_payload


def test_incident_permission_matrix(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(db_session, email="matrix-creator@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=creator.user_id)
    expected = {
        Role.ADMIN: {"create": 201, "read": 200, "update": 200, "delete": 200},
        Role.ANALYST: {"create": 201, "read": 200, "update": 200, "delete": 403},
        Role.VIEWER: {"create": 403, "read": 200, "update": 403, "delete": 403},
        Role.AUDITOR: {"create": 403, "read": 200, "update": 403, "delete": 403},
    }

    for role, statuses in expected.items():
        user = create_synthetic_user(
            db_session,
            email=f"incident-matrix-{role.value.lower()}@example.com",
            role=role,
        )
        header = bearer_header(test_settings, user)
        target = create_synthetic_incident(db_session, created_by=creator.user_id)

        assert (
            client.post("/incidents/", json=valid_payload(), headers=header).status_code
            == statuses["create"]
        )
        assert (
            client.get(f"/incidents/{incident.incident_id}", headers=header).status_code
            == statuses["read"]
        )
        assert (
            client.patch(
                f"/incidents/{incident.incident_id}",
                json={"title": "Matrix update title"},
                headers=header,
            ).status_code
            == statuses["update"]
        )
        assert (
            client.delete(f"/incidents/{target.incident_id}", headers=header).status_code
            == statuses["delete"]
        )

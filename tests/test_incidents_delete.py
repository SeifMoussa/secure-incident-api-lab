from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_admin_can_soft_delete_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="delete-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    original_updated_at = incident.updated_at

    response = client.delete(
        f"/incidents/{incident.incident_id}",
        headers=bearer_header(test_settings, admin),
    )

    db_session.refresh(incident)
    assert response.status_code == 200
    assert response.json()["message"] == "Incident deleted."
    assert incident.is_deleted is True
    assert incident.updated_at > original_updated_at


def test_delete_blocked_for_non_admin_roles(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(db_session, email="delete-creator@example.com", role=Role.ADMIN)

    for role in [Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        incident = create_synthetic_incident(db_session, created_by=creator.user_id)
        user = create_synthetic_user(
            db_session,
            email=f"delete-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.delete(
            f"/incidents/{incident.incident_id}",
            headers=bearer_header(test_settings, user),
        )

        assert response.status_code == 403

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_detail_returns_incident_for_read_roles(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(db_session, email="detail-creator@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=creator.user_id)

    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session,
            email=f"detail-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.get(
            f"/incidents/{incident.incident_id}",
            headers=bearer_header(test_settings, user),
        )

        assert response.status_code == 200
        assert response.json()["incident_id"] == incident.incident_id


def test_detail_returns_404_for_missing_or_soft_deleted_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="missing-detail-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    incident.is_deleted = True
    db_session.commit()
    header = bearer_header(test_settings, admin)

    assert client.get("/incidents/missing-id", headers=header).status_code == 404
    assert client.get(f"/incidents/{incident.incident_id}", headers=header).status_code == 404

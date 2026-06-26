from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import IncidentSeverity, IncidentStatus, Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_incident_filters(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="filter-admin@example.com", role=Role.ADMIN)
    assignee = create_synthetic_user(
        db_session, email="filter-assignee@example.com", role=Role.ANALYST
    )
    high = create_synthetic_incident(
        db_session,
        created_by=admin.user_id,
        assigned_to=assignee.user_id,
        severity=IncidentSeverity.HIGH,
        status=IncidentStatus.IN_PROGRESS,
        tags=["priority"],
    )
    low = create_synthetic_incident(
        db_session,
        created_by=admin.user_id,
        severity=IncidentSeverity.LOW,
        status=IncidentStatus.CLOSED,
        tags=["archive"],
    )
    high.created_at = datetime.now(UTC) - timedelta(days=1)
    low.created_at = datetime.now(UTC) - timedelta(days=10)
    db_session.commit()
    header = bearer_header(test_settings, admin)

    assert _ids(client.get("/incidents/?severity=HIGH", headers=header)) == [high.incident_id]
    assert _ids(client.get("/incidents/?status=IN_PROGRESS", headers=header)) == [high.incident_id]
    assert _ids(client.get(f"/incidents/?assigned_to={assignee.user_id}", headers=header)) == [
        high.incident_id
    ]
    assert _ids(client.get("/incidents/?tag=priority", headers=header)) == [high.incident_id]

    created_after = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    created_before = (datetime.now(UTC) - timedelta(days=2)).isoformat()
    assert _ids(
        client.get("/incidents/", params={"created_after": created_after}, headers=header)
    ) == [high.incident_id]
    assert _ids(
        client.get("/incidents/", params={"created_before": created_before}, headers=header)
    ) == [low.incident_id]


def _ids(response) -> list[str]:
    assert response.status_code == 200
    return [item["incident_id"] for item in response.json()["items"]]

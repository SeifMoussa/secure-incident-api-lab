from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import IncidentSeverity, Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_admin_and_analyst_can_update_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(db_session, email="update-creator@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=creator.user_id)

    for role in [Role.ADMIN, Role.ANALYST]:
        user = create_synthetic_user(
            db_session,
            email=f"update-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.patch(
            f"/incidents/{incident.incident_id}",
            json={"title": f"Updated by {role.value}", "severity": "CRITICAL"},
            headers=bearer_header(test_settings, user),
        )

        assert response.status_code == 200
        assert response.json()["severity"] == "CRITICAL"


def test_viewer_and_auditor_cannot_update_incident(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(
        db_session, email="blocked-update-creator@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=creator.user_id)

    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session,
            email=f"blocked-update-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.patch(
            f"/incidents/{incident.incident_id}",
            json={"title": "Blocked update"},
            headers=bearer_header(test_settings, user),
        )

        assert response.status_code == 403


def test_update_only_allows_selected_fields_and_updates_timestamp(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="allowed-update-admin@example.com", role=Role.ADMIN
    )
    assignee = create_synthetic_user(
        db_session, email="allowed-update-assignee@example.com", role=Role.ANALYST
    )
    incident = create_synthetic_incident(
        db_session,
        created_by=admin.user_id,
        severity=IncidentSeverity.LOW,
    )
    original_created_by = incident.created_by
    original_updated_at = incident.updated_at

    blocked_response = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"created_by": assignee.user_id, "is_deleted": True},
        headers=bearer_header(test_settings, admin),
    )
    allowed_response = client.patch(
        f"/incidents/{incident.incident_id}",
        json={
            "title": "Updated synthetic incident",
            "assigned_to": assignee.user_id,
            "mitre_tactic": "discovery",
            "mitre_technique": "T1087",
            "tags": ["Updated"],
        },
        headers=bearer_header(test_settings, admin),
    )

    db_session.refresh(incident)
    assert blocked_response.status_code == 422
    assert allowed_response.status_code == 200
    assert incident.created_by == original_created_by
    assert incident.is_deleted is False
    assert incident.updated_at > original_updated_at
    assert allowed_response.json()["tags"] == ["updated"]

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import IncidentStatus, Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_new_open_incident_has_no_sla_timestamps_set(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="sla-new-admin@example.com", role=Role.ADMIN)

    response = client.post(
        "/incidents/",
        json={
            "title": "Synthetic SLA incident",
            "description": "Synthetic defensive incident for SLA tests.",
            "severity": "HIGH",
            "status": "OPEN",
        },
        headers=bearer_header(test_settings, admin),
    )

    body = response.json()
    assert response.status_code == 201
    assert body["acknowledged_at"] is None
    assert body["resolved_at"] is None
    assert body["time_to_acknowledge_seconds"] is None
    assert body["time_to_resolve_seconds"] is None
    assert body["age_in_status_seconds"] >= 0


def test_creating_incident_with_non_open_status_stamps_timestamps_immediately(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="sla-create-resolved@example.com", role=Role.ADMIN
    )

    response = client.post(
        "/incidents/",
        json={
            "title": "Pre-resolved synthetic incident",
            "description": "Created directly in a resolved state for test-only use.",
            "severity": "LOW",
            "status": "RESOLVED",
        },
        headers=bearer_header(test_settings, admin),
    )

    body = response.json()
    assert response.status_code == 201
    assert body["acknowledged_at"] is not None
    assert body["resolved_at"] is not None
    assert body["time_to_acknowledge_seconds"] == 0
    assert body["time_to_resolve_seconds"] == 0


def test_acknowledged_at_is_set_once_and_survives_further_status_changes(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="sla-ack-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    first = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"status": "IN_PROGRESS"},
        headers=bearer_header(test_settings, admin),
    )
    first_acknowledged_at = first.json()["acknowledged_at"]

    second = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"status": "CONTAINED"},
        headers=bearer_header(test_settings, admin),
    )

    assert first.status_code == 200
    assert first_acknowledged_at is not None
    assert first.json()["time_to_acknowledge_seconds"] is not None
    assert second.status_code == 200
    assert second.json()["acknowledged_at"] == first_acknowledged_at


def test_resolved_at_clears_when_incident_is_reopened(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="sla-reopen-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    resolved = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"status": "RESOLVED"},
        headers=bearer_header(test_settings, admin),
    )
    reopened = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"status": "IN_PROGRESS"},
        headers=bearer_header(test_settings, admin),
    )

    assert resolved.json()["resolved_at"] is not None
    assert resolved.json()["time_to_resolve_seconds"] is not None
    assert reopened.status_code == 200
    assert reopened.json()["resolved_at"] is None
    assert reopened.json()["time_to_resolve_seconds"] is None
    # Already-acknowledged incidents stay acknowledged after reopening.
    assert reopened.json()["acknowledged_at"] is not None


def test_status_changed_at_only_moves_on_actual_status_transitions(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="sla-nochange-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    unrelated_update = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"title": "Title only, no status change"},
        headers=bearer_header(test_settings, admin),
    )

    assert unrelated_update.status_code == 200
    assert unrelated_update.json()["acknowledged_at"] is None
    assert unrelated_update.json()["resolved_at"] is None


def test_incident_response_model_exposes_all_new_sla_fields(db_session: Session) -> None:
    admin_email = "sla-model-fields@example.com"
    from app.auth.models import User

    user = User(email=admin_email, display_name="SLA Model", password_hash="synthetic-hash-only")
    db_session.add(user)
    db_session.flush()
    incident = create_synthetic_incident(
        db_session, created_by=user.user_id, status=IncidentStatus.OPEN
    )

    columns = set(incident.__table__.columns.keys())
    assert {"status_changed_at", "acknowledged_at", "resolved_at"} <= columns

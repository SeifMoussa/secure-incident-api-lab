from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_incident_timeline_returns_incident_audit_entries_oldest_first(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "timeline-admin@example.com")
    incident = create_incident_via_api(client, test_settings, admin)
    incident_id = str(incident["incident_id"])
    headers = bearer_header(test_settings, admin)
    client.patch(f"/incidents/{incident_id}", json={"status": "CONTAINED"}, headers=headers)
    client.delete(f"/incidents/{incident_id}", headers=headers)

    response = client.get(f"/incidents/{incident_id}/timeline", headers=headers)

    assert response.status_code == 404


def test_incident_timeline_for_active_incident_all_read_roles(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "timeline-read-admin@example.com")
    incident = create_incident_via_api(client, test_settings, admin)
    incident_id = str(incident["incident_id"])
    client.patch(
        f"/incidents/{incident_id}",
        json={"status": "CONTAINED"},
        headers=bearer_header(test_settings, admin),
    )

    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = (
            admin
            if role == Role.ADMIN
            else create_synthetic_user(
                db_session,
                email=f"timeline-{role.value.lower()}@example.com",
                role=role,
            )
        )
        response = client.get(
            f"/incidents/{incident_id}/timeline",
            headers=bearer_header(test_settings, user),
        )
        assert response.status_code == 200
        body = response.json()
        assert body["incident_id"] == incident_id
        assert [item["action"] for item in body["items"]] == ["CREATE", "UPDATE"]
        assert all(item["resource_type"] == "incident" for item in body["items"])


def test_incident_timeline_missing_and_soft_deleted_incident_returns_404(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "timeline-missing-admin@example.com")
    deleted = create_synthetic_incident(db_session, created_by=admin.user_id)
    deleted.is_deleted = True
    db_session.commit()
    headers = bearer_header(test_settings, admin)

    assert client.get("/incidents/not-a-real-id/timeline", headers=headers).status_code == 404
    deleted_response = client.get(f"/incidents/{deleted.incident_id}/timeline", headers=headers)
    assert deleted_response.status_code == 404


def test_incident_timeline_response_is_sanitized(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "timeline-safety-admin@example.com")
    incident = create_incident_via_api(client, test_settings, admin)

    response = client.get(
        f"/incidents/{incident['incident_id']}/timeline",
        headers=bearer_header(test_settings, admin),
    )

    forbidden = ["password_hash", "access_token", "refresh_token", "Authorization", "api_key"]
    assert all(value not in response.text for value in forbidden)

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_remediation_create import remediation_payload


def _create_task(client: TestClient, settings: Settings, user, incident_id: str) -> dict:
    response = client.post(
        f"/incidents/{incident_id}/remediation/",
        json=remediation_payload(),
        headers=bearer_header(settings, user),
    )
    assert response.status_code == 201
    return response.json()


def test_remediation_list_update_delete_and_status_transitions(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="rem-list-admin@example.com", role=Role.ADMIN)
    analyst = create_synthetic_user(
        db_session, email="rem-list-analyst@example.com", role=Role.ANALYST
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    task = _create_task(client, test_settings, admin, incident.incident_id)
    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"rem-read-{role.value.lower()}@example.com", role=role
        )
        assert (
            client.get(
                f"/incidents/{incident.incident_id}/remediation/",
                headers=bearer_header(test_settings, user),
            ).status_code
            == 200
        )
    complete = client.patch(
        f"/incidents/{incident.incident_id}/remediation/{task['task_id']}",
        json={"status": "COMPLETE"},
        headers=bearer_header(test_settings, analyst),
    )
    assert complete.status_code == 200
    assert complete.json()["completed_at"] is not None
    reopened = client.patch(
        f"/incidents/{incident.incident_id}/remediation/{task['task_id']}",
        json={"status": "IN_PROGRESS"},
        headers=bearer_header(test_settings, analyst),
    )
    assert reopened.status_code == 200
    assert reopened.json()["completed_at"] is None
    assert (
        client.delete(
            f"/incidents/{incident.incident_id}/remediation/{task['task_id']}",
            headers=bearer_header(test_settings, analyst),
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/incidents/{incident.incident_id}/remediation/",
            headers=bearer_header(test_settings, admin),
        ).json()["total"]
        == 0
    )


def test_remediation_update_delete_rbac(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(db_session, email="rem-matrix-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    for role, expected in {
        Role.ADMIN: 200,
        Role.ANALYST: 200,
        Role.VIEWER: 403,
        Role.AUDITOR: 403,
    }.items():
        task = _create_task(client, test_settings, admin, incident.incident_id)
        user = (
            admin
            if role == Role.ADMIN
            else create_synthetic_user(
                db_session,
                email=f"rem-matrix-{role.value.lower()}@example.com",
                role=role,
            )
        )
        assert (
            client.patch(
                f"/incidents/{incident.incident_id}/remediation/{task['task_id']}",
                json={"action": "Updated synthetic action."},
                headers=bearer_header(test_settings, user),
            ).status_code
            == expected
        )
        assert (
            client.delete(
                f"/incidents/{incident.incident_id}/remediation/{task['task_id']}",
                headers=bearer_header(test_settings, user),
            ).status_code
            == expected
        )

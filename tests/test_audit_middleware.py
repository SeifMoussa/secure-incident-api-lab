from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import AuditAction, AuditOutcome, Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user
from tests.test_audit_helpers import audit_entries, create_admin, create_incident_via_api


def test_register_login_logout_create_sanitized_audit_entries(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": "audit-register@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Audit Register",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "audit-register@example.com", "password": TEST_ONLY_PASSWORD},
    )
    assert login_response.status_code == 200

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": login_response.json()["refresh_token"]},
    )
    assert logout_response.status_code == 200

    entries = audit_entries(db_session)
    assert [entry.action for entry in entries] == [
        AuditAction.CREATE,
        AuditAction.LOGIN,
        AuditAction.LOGOUT,
    ]
    assert all(entry.outcome == AuditOutcome.SUCCESS for entry in entries)
    combined = "".join(str(entry.changes) for entry in entries)
    assert TEST_ONLY_PASSWORD not in combined
    assert login_response.json()["access_token"] not in combined
    assert login_response.json()["refresh_token"] not in combined
    assert entries[0].actor_id == register_response.json()["user_id"]
    assert entries[1].actor_id == register_response.json()["user_id"]


def test_login_failure_creates_failure_audit_without_actor(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "missing-audit-user@example.com", "password": TEST_ONLY_PASSWORD},
    )

    assert response.status_code == 401
    entry = audit_entries(db_session)[0]
    assert entry.action == AuditAction.LOGIN
    assert entry.outcome == AuditOutcome.FAILURE
    assert entry.actor_id is None
    assert TEST_ONLY_PASSWORD not in str(entry.changes)


def test_incident_and_nested_writes_create_audit_entries(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session)
    incident = create_incident_via_api(client, test_settings, admin)
    incident_id = str(incident["incident_id"])
    headers = bearer_header(test_settings, admin)

    client.patch(
        f"/incidents/{incident_id}",
        json={"status": "CONTAINED"},
        headers=headers,
    )
    ticket = client.post(
        f"/incidents/{incident_id}/tickets/",
        json={
            "title": "Synthetic ticket",
            "description": "Synthetic ticket for audit.",
            "status": "OPEN",
            "priority": "P2",
        },
        headers=headers,
    ).json()
    evidence = client.post(
        f"/incidents/{incident_id}/evidence/",
        json={
            "content": "Synthetic markdown evidence note",
            "source": "synthetic",
            "collected_at": "2026-01-01T00:00:00Z",
            "tags": ["audit"],
        },
        headers=headers,
    ).json()
    remediation = client.post(
        f"/incidents/{incident_id}/remediation/",
        json={"action": "Synthetic containment action", "status": "PENDING"},
        headers=headers,
    ).json()
    client.delete(f"/incidents/{incident_id}/tickets/{ticket['ticket_id']}", headers=headers)
    client.patch(
        f"/incidents/{incident_id}/evidence/{evidence['evidence_id']}",
        json={"source": "updated synthetic"},
        headers=headers,
    )
    client.patch(
        f"/incidents/{incident_id}/remediation/{remediation['task_id']}",
        json={"status": "COMPLETE"},
        headers=headers,
    )
    client.delete(f"/incidents/{incident_id}", headers=headers)

    entries = audit_entries(db_session)
    assert {entry.resource_type for entry in entries} == {
        "incident",
        "ticket",
        "evidence",
        "remediation",
    }
    assert {AuditAction.CREATE, AuditAction.UPDATE, AuditAction.DELETE}.issubset(
        {entry.action for entry in entries}
    )
    assert all(entry.actor_id == admin.user_id for entry in entries)


def test_failed_unauthorized_write_creates_failure_audit(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    viewer = create_synthetic_user(
        db_session, email="audit-failure-viewer@example.com", role=Role.VIEWER
    )

    response = client.post(
        "/incidents/",
        json={
            "title": "Blocked synthetic incident",
            "description": "Synthetic incident that should be forbidden.",
            "severity": "LOW",
            "status": "OPEN",
        },
        headers=bearer_header(test_settings, viewer),
    )

    assert response.status_code == 403
    entry = audit_entries(db_session)[0]
    assert entry.action == AuditAction.CREATE
    assert entry.resource_type == "incident"
    assert entry.outcome == AuditOutcome.FAILURE
    assert entry.actor_id == viewer.user_id

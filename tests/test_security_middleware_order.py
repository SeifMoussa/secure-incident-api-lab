from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import AuditAction, Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user
from tests.test_audit_helpers import audit_entries, create_admin, create_incident_via_api


def test_existing_auth_and_domain_flows_still_work_with_security_middleware(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    register = client.post(
        "/auth/register",
        json={
            "email": "security-flow-user@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Security Flow User",
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        json={"email": "security-flow-user@example.com", "password": TEST_ONLY_PASSWORD},
    )
    assert login.status_code == 200
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert me.status_code == 200

    admin = create_admin(db_session, "security-flow-admin@example.com")
    analyst = create_synthetic_user(
        db_session, email="security-flow-analyst@example.com", role=Role.ANALYST
    )
    incident = create_incident_via_api(client, test_settings, admin)
    incident_id = str(incident["incident_id"])
    analyst_headers = bearer_header(test_settings, analyst)

    ticket = client.post(
        f"/incidents/{incident_id}/tickets/",
        json={
            "title": "Synthetic security middleware ticket",
            "description": "Synthetic ticket for middleware compatibility.",
            "status": "OPEN",
            "priority": "P3",
        },
        headers=analyst_headers,
    )
    evidence = client.post(
        f"/incidents/{incident_id}/evidence/",
        json={
            "content": "Synthetic middleware evidence note",
            "source": "synthetic",
            "collected_at": "2026-01-01T00:00:00Z",
        },
        headers=analyst_headers,
    )
    remediation = client.post(
        f"/incidents/{incident_id}/remediation/",
        json={"action": "Synthetic middleware remediation", "status": "PENDING"},
        headers=analyst_headers,
    )

    assert ticket.status_code == 201
    assert evidence.status_code == 201
    assert remediation.status_code == 201
    timeline = client.get(
        f"/incidents/{incident_id}/timeline",
        headers=bearer_header(test_settings, admin),
    )
    assert timeline.status_code == 200


def test_audit_still_records_write_requests_with_security_middleware(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "security-audit-admin@example.com")
    create_incident_via_api(client, test_settings, admin)

    entries = audit_entries(db_session)

    assert any(entry.action == AuditAction.CREATE for entry in entries)
    assert all("access_token" not in str(entry.changes) for entry in entries)

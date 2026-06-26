from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_audit_helpers import audit_entries
from tests.test_evidence_create import evidence_payload
from tests.test_remediation_create import remediation_payload
from tests.test_tickets_create import ticket_payload

SECRET_LIKE = "Bearer aaaaaaaa.bbbbbbbb.cccccccc"


def assert_audit_log_redacted(db_session: Session) -> None:
    combined = " ".join(str(entry.changes) for entry in audit_entries(db_session)).lower()
    forbidden = [
        TEST_ONLY_PASSWORD.lower(),
        "password_hash",
        "access_token",
        "refresh_token",
        "authorization",
        "bearer ",
        "api_key",
        "jwt_secret",
        "cookie",
        "set-cookie",
        "aaaaaaaa.bbbbbbbb.cccccccc",
    ]
    for value in forbidden:
        assert value not in combined


def test_audit_redaction_for_auth_and_logout_flows(
    client: TestClient,
    db_session: Session,
) -> None:
    register = client.post(
        "/auth/register",
        json={
            "email": "audit-redaction-auth@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Audit Redaction",
        },
    )
    login = client.post(
        "/auth/login",
        json={"email": "audit-redaction-auth@example.com", "password": TEST_ONLY_PASSWORD},
    )
    refresh = client.post("/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
    logout = client.post("/auth/logout", json={"refresh_token": login.json()["refresh_token"]})

    assert [register.status_code, login.status_code, refresh.status_code, logout.status_code] == [
        201,
        200,
        200,
        200,
    ]
    assert_audit_log_redacted(db_session)
    assert all(entry.action != "REFRESH" for entry in audit_entries(db_session))


def test_audit_redaction_for_domain_writes_and_failed_write(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="audit-redaction-admin@example.com", role=Role.ADMIN
    )
    viewer = create_synthetic_user(
        db_session, email="audit-redaction-viewer@example.com", role=Role.VIEWER
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    admin_headers = bearer_header(test_settings, admin)
    viewer_headers = bearer_header(test_settings, viewer)

    client.post(
        "/incidents/",
        json={
            "title": "Synthetic audit redaction incident",
            "description": SECRET_LIKE,
            "severity": "LOW",
            "status": "OPEN",
        },
        headers=admin_headers,
    )
    client.post(
        f"/incidents/{incident.incident_id}/tickets/",
        json=ticket_payload(description=SECRET_LIKE),
        headers=admin_headers,
    )
    client.post(
        f"/incidents/{incident.incident_id}/evidence/",
        json=evidence_payload(content=SECRET_LIKE),
        headers=admin_headers,
    )
    client.post(
        f"/incidents/{incident.incident_id}/remediation/",
        json=remediation_payload(action=SECRET_LIKE),
        headers=admin_headers,
    )
    client.post(
        "/incidents/",
        json={
            "title": "Synthetic blocked write",
            "description": SECRET_LIKE,
            "severity": "LOW",
            "status": "OPEN",
        },
        headers=viewer_headers,
    )

    assert_audit_log_redacted(db_session)

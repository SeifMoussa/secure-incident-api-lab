from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_create import evidence_payload
from tests.test_remediation_create import remediation_payload
from tests.test_tickets_create import ticket_payload

PROTECTED_FIELDS = {
    "user_id": "synthetic-user-id",
    "password_hash": "synthetic-hash",
    "is_active": True,
    "created_at": datetime.now(UTC).isoformat(),
    "updated_at": datetime.now(UTC).isoformat(),
    "created_by": "synthetic-creator",
    "is_deleted": True,
    "audit_id": "synthetic-audit",
    "outcome": "SUCCESS",
}


def test_register_rejects_privilege_and_identity_mass_assignment(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "mass-register@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Mass Register",
            "role": "ADMIN",
            "password_hash": "synthetic-hash",
            "is_active": True,
            "user_id": "synthetic-user-id",
        },
    )

    assert response.status_code == 422


def test_admin_role_update_rejects_extra_protected_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="mass-admin@example.com", role=Role.ADMIN)
    target = create_synthetic_user(db_session, email="mass-target@example.com", role=Role.VIEWER)

    response = client.patch(
        f"/admin/users/{target.user_id}/role",
        json={"role": "ANALYST", "password_hash": "synthetic-hash", "is_active": True},
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 422


def test_incident_create_and_update_reject_server_managed_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="mass-incident-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    headers = bearer_header(test_settings, admin)
    create_payload = {
        "title": "Synthetic mass assignment incident",
        "description": "Synthetic defensive test.",
        "severity": "LOW",
        "status": "OPEN",
        **PROTECTED_FIELDS,
        "incident_id": incident.incident_id,
    }

    create_response = client.post("/incidents/", json=create_payload, headers=headers)
    update_response = client.patch(
        f"/incidents/{incident.incident_id}",
        json={"title": "Synthetic updated incident", "created_by": admin.user_id},
        headers=headers,
    )

    assert create_response.status_code == 422
    assert update_response.status_code == 422


def test_nested_create_and_update_reject_server_managed_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="mass-nested-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    headers = bearer_header(test_settings, admin)
    ticket = client.post(
        f"/incidents/{incident.incident_id}/tickets/",
        json=ticket_payload(),
        headers=headers,
    ).json()
    evidence = client.post(
        f"/incidents/{incident.incident_id}/evidence/",
        json=evidence_payload(),
        headers=headers,
    ).json()
    remediation = client.post(
        f"/incidents/{incident.incident_id}/remediation/",
        json=remediation_payload(),
        headers=headers,
    ).json()

    cases = [
        (
            "post",
            f"/incidents/{incident.incident_id}/tickets/",
            ticket_payload(ticket_id=ticket["ticket_id"], created_by=admin.user_id),
        ),
        (
            "patch",
            f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}",
            {"title": "Synthetic ticket update", "is_deleted": True},
        ),
        (
            "post",
            f"/incidents/{incident.incident_id}/evidence/",
            evidence_payload(evidence_id=evidence["evidence_id"], attachment_id="synthetic"),
        ),
        (
            "patch",
            f"/incidents/{incident.incident_id}/evidence/{evidence['evidence_id']}",
            {"source": "synthetic-updated", "created_by": admin.user_id},
        ),
        (
            "post",
            f"/incidents/{incident.incident_id}/remediation/",
            remediation_payload(
                task_id=remediation["task_id"], completed_at=datetime.now(UTC).isoformat()
            ),
        ),
        (
            "patch",
            f"/incidents/{incident.incident_id}/remediation/{remediation['task_id']}",
            {"status": "COMPLETE", "completed_at": datetime.now(UTC).isoformat()},
        ),
    ]

    for method, url, payload in cases:
        response = getattr(client, method)(url, json=payload, headers=headers)
        assert response.status_code == 422

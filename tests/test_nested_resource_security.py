from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_create import evidence_payload
from tests.test_remediation_create import remediation_payload
from tests.test_tickets_create import ticket_payload


def test_nested_resources_under_wrong_incident_return_404(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="nested-wrong-admin@example.com", role=Role.ADMIN
    )
    first = create_synthetic_incident(db_session, created_by=admin.user_id)
    second = create_synthetic_incident(db_session, created_by=admin.user_id)
    headers = bearer_header(test_settings, admin)
    ticket = client.post(
        f"/incidents/{first.incident_id}/tickets/", json=ticket_payload(), headers=headers
    ).json()
    evidence = client.post(
        f"/incidents/{first.incident_id}/evidence/", json=evidence_payload(), headers=headers
    ).json()
    remediation = client.post(
        f"/incidents/{first.incident_id}/remediation/", json=remediation_payload(), headers=headers
    ).json()

    wrong_ticket = client.get(
        f"/incidents/{second.incident_id}/tickets/{ticket['ticket_id']}", headers=headers
    )
    wrong_evidence = client.get(
        f"/incidents/{second.incident_id}/evidence/{evidence['evidence_id']}", headers=headers
    )
    wrong_remediation = client.patch(
        f"/incidents/{second.incident_id}/remediation/{remediation['task_id']}",
        json={"status": "COMPLETE"},
        headers=headers,
    )
    assert wrong_ticket.status_code == 404
    assert wrong_evidence.status_code == 404
    assert wrong_remediation.status_code == 404


def test_soft_deleted_parent_and_nested_resources_block_access(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="nested-soft-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    headers = bearer_header(test_settings, admin)
    ticket = client.post(
        f"/incidents/{incident.incident_id}/tickets/", json=ticket_payload(), headers=headers
    ).json()
    evidence = client.post(
        f"/incidents/{incident.incident_id}/evidence/", json=evidence_payload(), headers=headers
    ).json()
    remediation = client.post(
        f"/incidents/{incident.incident_id}/remediation/",
        json=remediation_payload(),
        headers=headers,
    ).json()

    ticket_delete = client.delete(
        f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}", headers=headers
    )
    evidence_delete = client.delete(
        f"/incidents/{incident.incident_id}/evidence/{evidence['evidence_id']}", headers=headers
    )
    remediation_delete = client.delete(
        f"/incidents/{incident.incident_id}/remediation/{remediation['task_id']}",
        headers=headers,
    )
    assert ticket_delete.status_code == 200
    assert evidence_delete.status_code == 200
    assert remediation_delete.status_code == 200

    deleted_ticket = client.get(
        f"/incidents/{incident.incident_id}/tickets/{ticket['ticket_id']}", headers=headers
    )
    deleted_evidence = client.patch(
        f"/incidents/{incident.incident_id}/evidence/{evidence['evidence_id']}",
        json={"source": "synthetic"},
        headers=headers,
    )
    deleted_remediation = client.delete(
        f"/incidents/{incident.incident_id}/remediation/{remediation['task_id']}",
        headers=headers,
    )
    assert deleted_ticket.status_code == 404
    assert deleted_evidence.status_code == 404
    assert deleted_remediation.status_code == 404

    parent = create_synthetic_incident(db_session, created_by=admin.user_id)
    parent.is_deleted = True
    db_session.commit()
    parent_tickets = client.get(f"/incidents/{parent.incident_id}/tickets/", headers=headers)
    parent_evidence = client.get(f"/incidents/{parent.incident_id}/evidence/", headers=headers)
    parent_remediation = client.get(
        f"/incidents/{parent.incident_id}/remediation/", headers=headers
    )
    assert parent_tickets.status_code == 404
    assert parent_evidence.status_code == 404
    assert parent_remediation.status_code == 404


def test_nested_resource_role_and_owner_security_regressions(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="nested-role-admin@example.com", role=Role.ADMIN
    )
    analyst_owner = create_synthetic_user(
        db_session, email="nested-role-owner@example.com", role=Role.ANALYST
    )
    analyst_other = create_synthetic_user(
        db_session, email="nested-role-other@example.com", role=Role.ANALYST
    )
    inactive = create_synthetic_user(
        db_session, email="nested-role-inactive@example.com", role=Role.ANALYST, is_active=False
    )
    viewer = create_synthetic_user(
        db_session, email="nested-role-viewer@example.com", role=Role.VIEWER
    )
    auditor = create_synthetic_user(
        db_session, email="nested-role-auditor@example.com", role=Role.AUDITOR
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    admin_headers = bearer_header(test_settings, admin)
    owner_headers = bearer_header(test_settings, analyst_owner)
    other_headers = bearer_header(test_settings, analyst_other)
    evidence = client.post(
        f"/incidents/{incident.incident_id}/evidence/",
        json=evidence_payload(),
        headers=owner_headers,
    ).json()

    inactive_ticket = client.post(
        f"/incidents/{incident.incident_id}/tickets/",
        json=ticket_payload(assigned_to=inactive.user_id),
        headers=admin_headers,
    )
    inactive_remediation = client.post(
        f"/incidents/{incident.incident_id}/remediation/",
        json=remediation_payload(owner=inactive.user_id),
        headers=admin_headers,
    )
    other_analyst_update = client.patch(
        f"/incidents/{incident.incident_id}/evidence/{evidence['evidence_id']}",
        json={"source": "synthetic-other"},
        headers=other_headers,
    )
    assert inactive_ticket.status_code == 404
    assert inactive_remediation.status_code == 404
    assert other_analyst_update.status_code == 403
    for user in [viewer, auditor]:
        response = client.post(
            f"/incidents/{incident.incident_id}/tickets/",
            json=ticket_payload(),
            headers=bearer_header(test_settings, user),
        )
        assert response.status_code == 403

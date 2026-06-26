from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def remediation_payload(**overrides):
    payload = {
        "action": "Perform synthetic containment follow-up.",
        "status": "PENDING",
        "completion_notes": "Synthetic note.",
    }
    payload.update(overrides)
    return payload


def test_remediation_create_and_owner_validation(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(db_session, email="rem-create-admin@example.com", role=Role.ADMIN)
    owner = create_synthetic_user(db_session, email="rem-owner@example.com", role=Role.ANALYST)
    inactive = create_synthetic_user(
        db_session, email="rem-inactive@example.com", role=Role.ANALYST, is_active=False
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    assert (
        client.post(
            f"/incidents/{incident.incident_id}/remediation/",
            json=remediation_payload(owner=owner.user_id),
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 201
    )
    assert (
        client.post(
            f"/incidents/{incident.incident_id}/remediation/",
            json=remediation_payload(owner=inactive.user_id),
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 404
    )


def test_remediation_create_rbac_and_validation(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(db_session, email="rem-rbac-admin@example.com", role=Role.ADMIN)
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"rem-deny-{role.value.lower()}@example.com", role=role
        )
        assert (
            client.post(
                f"/incidents/{incident.incident_id}/remediation/",
                json=remediation_payload(),
                headers=bearer_header(test_settings, user),
            ).status_code
            == 403
        )
    for payload in [
        remediation_payload(action=""),
        remediation_payload(status="UNKNOWN"),
        remediation_payload(completion_notes="x" * 2001),
    ]:
        assert (
            client.post(
                f"/incidents/{incident.incident_id}/remediation/",
                json=payload,
                headers=bearer_header(test_settings, admin),
            ).status_code
            == 422
        )

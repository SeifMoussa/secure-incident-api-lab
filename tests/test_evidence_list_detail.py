from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_create import evidence_payload


def _create_note(client: TestClient, settings: Settings, user, incident_id: str) -> dict:
    response = client.post(
        f"/incidents/{incident_id}/evidence/",
        json=evidence_payload(),
        headers=bearer_header(settings, user),
    )
    assert response.status_code == 201
    return response.json()


def test_evidence_list_detail_all_roles_and_scoping(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="evidence-list-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    other = create_synthetic_incident(db_session, created_by=admin.user_id)
    note = _create_note(client, test_settings, admin, incident.incident_id)
    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"evidence-read-{role.value.lower()}@example.com", role=role
        )
        header = bearer_header(test_settings, user)
        assert (
            client.get(f"/incidents/{incident.incident_id}/evidence/", headers=header).status_code
            == 200
        )
        assert (
            client.get(
                f"/incidents/{incident.incident_id}/evidence/{note['evidence_id']}", headers=header
            ).status_code
            == 200
        )
    assert (
        client.get(
            f"/incidents/{other.incident_id}/evidence/{note['evidence_id']}",
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 404
    )

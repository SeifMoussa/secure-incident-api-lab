from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_list_detail import _create_note


def test_evidence_update_delete_rules(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="evidence-update-admin@example.com", role=Role.ADMIN
    )
    analyst = create_synthetic_user(
        db_session, email="evidence-update-analyst@example.com", role=Role.ANALYST
    )
    other_analyst = create_synthetic_user(
        db_session, email="evidence-other-analyst@example.com", role=Role.ANALYST
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    own = _create_note(client, test_settings, analyst, incident.incident_id)
    other = _create_note(client, test_settings, other_analyst, incident.incident_id)
    own_update = client.patch(
        f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
        json={"content": "Updated synthetic evidence"},
        headers=bearer_header(test_settings, analyst),
    )
    other_update = client.patch(
        f"/incidents/{incident.incident_id}/evidence/{other['evidence_id']}",
        json={"content": "Blocked synthetic evidence update"},
        headers=bearer_header(test_settings, analyst),
    )
    assert own_update.status_code == 200
    assert other_update.status_code == 403
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"evidence-update-{role.value.lower()}@example.com", role=role
        )
        response = client.patch(
            f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
            json={"content": "Blocked"},
            headers=bearer_header(test_settings, user),
        )
        assert response.status_code == 403
    analyst_delete = client.delete(
        f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
        headers=bearer_header(test_settings, analyst),
    )
    admin_delete = client.delete(
        f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
        headers=bearer_header(test_settings, admin),
    )
    remaining = client.get(
        f"/incidents/{incident.incident_id}/evidence/",
        headers=bearer_header(test_settings, admin),
    )

    assert analyst_delete.status_code == 403
    assert admin_delete.status_code == 200
    assert remaining.json()["total"] == 1

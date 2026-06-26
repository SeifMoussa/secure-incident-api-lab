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
    assert (
        client.patch(
            f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
            json={"content": "Updated synthetic evidence"},
            headers=bearer_header(test_settings, analyst),
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"/incidents/{incident.incident_id}/evidence/{other['evidence_id']}",
            json={"content": "Blocked synthetic evidence update"},
            headers=bearer_header(test_settings, analyst),
        ).status_code
        == 403
    )
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"evidence-update-{role.value.lower()}@example.com", role=role
        )
        assert (
            client.patch(
                f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
                json={"content": "Blocked"},
                headers=bearer_header(test_settings, user),
            ).status_code
            == 403
        )
    assert (
        client.delete(
            f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
            headers=bearer_header(test_settings, analyst),
        ).status_code
        == 403
    )
    assert (
        client.delete(
            f"/incidents/{incident.incident_id}/evidence/{own['evidence_id']}",
            headers=bearer_header(test_settings, admin),
        ).status_code
        == 200
    )
    assert (
        client.get(
            f"/incidents/{incident.incident_id}/evidence/",
            headers=bearer_header(test_settings, admin),
        ).json()["total"]
        == 1
    )

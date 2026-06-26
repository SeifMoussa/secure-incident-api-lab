from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_create import evidence_payload
from tests.test_remediation_create import remediation_payload
from tests.test_tickets_create import ticket_payload


def test_nested_resource_responses_do_not_include_sensitive_values(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="nested-safety-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    header = bearer_header(test_settings, admin)
    responses = [
        client.post(
            f"/incidents/{incident.incident_id}/tickets/", json=ticket_payload(), headers=header
        ),
        client.post(
            f"/incidents/{incident.incident_id}/evidence/", json=evidence_payload(), headers=header
        ),
        client.post(
            f"/incidents/{incident.incident_id}/remediation/",
            json=remediation_payload(),
            headers=header,
        ),
    ]
    combined = "".join(response.text for response in responses)
    assert "password_hash" not in combined
    assert "password" not in combined
    assert "access_token" not in combined
    assert "refresh_token" not in combined
    assert "authorization" not in combined.lower()
    assert test_settings.jwt_secret_key not in combined


def test_no_legacy_rate_limit_or_security_header_paths_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    forbidden_paths = [
        "app/security_headers.py",
        "app/rate_limit.py",
    ]
    for relative_path in forbidden_paths:
        assert not (root / relative_path).exists(), relative_path

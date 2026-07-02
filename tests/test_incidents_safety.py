from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_incident_responses_do_not_include_sensitive_values(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="incident-safety-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)

    list_response = client.get("/incidents/", headers=bearer_header(test_settings, admin))
    detail_response = client.get(
        f"/incidents/{incident.incident_id}",
        headers=bearer_header(test_settings, admin),
    )
    combined_text = list_response.text + detail_response.text

    assert "password_hash" not in combined_text
    assert "password" not in combined_text
    assert "access_token" not in combined_text
    assert "refresh_token" not in combined_text
    assert test_settings.jwt_secret_key not in combined_text


def test_no_legacy_security_module_paths_exist() -> None:
    root = Path(__file__).resolve().parents[1]
    forbidden_paths = [
        "app/security_headers.py",
        "app/rate_limit.py",
    ]

    for relative_path in forbidden_paths:
        assert not (root / relative_path).exists(), relative_path

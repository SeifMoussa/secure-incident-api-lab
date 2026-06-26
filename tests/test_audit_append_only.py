from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from tests.auth_test_helpers import bearer_header
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_audit_log_is_append_only_at_api_level(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-append-admin@example.com")
    create_incident_via_api(client, test_settings, admin)
    headers = bearer_header(test_settings, admin)

    assert client.post("/audit/", json={}, headers=headers).status_code in {404, 405}
    assert client.patch("/audit/synthetic-id", json={}, headers=headers).status_code in {404, 405}
    assert client.delete("/audit/synthetic-id", headers=headers).status_code in {404, 405}


def test_no_security_or_ci_files_added_for_phase_7() -> None:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    assert not (project_root / "app" / "security_headers.py").exists()
    assert not (project_root / "app" / "rate_limit.py").exists()
    assert not (project_root / ".git" / "HEAD").exists()

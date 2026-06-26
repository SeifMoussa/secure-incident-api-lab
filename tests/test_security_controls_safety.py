from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header
from tests.test_audit_helpers import audit_entries, create_admin


def test_security_control_responses_do_not_leak_sensitive_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "security-safety-admin@example.com")
    login = client.post(
        "/auth/login",
        json={"email": admin.email, "password": TEST_ONLY_PASSWORD},
    )
    me = client.get("/auth/me", headers=bearer_header(test_settings, admin))

    assert login.status_code == 200
    assert me.status_code == 200
    forbidden = ["password_hash", TEST_ONLY_PASSWORD, "api_key", "jwt_secret"]
    assert all(value not in me.text for value in forbidden)
    assert "access_token" in login.text
    assert "refresh_token" in login.text


def test_audit_logs_still_do_not_include_token_values(
    client: TestClient,
    db_session: Session,
) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "security-audit-safety@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Audit Safety User",
        },
    )
    assert response.status_code == 201
    login = client.post(
        "/auth/login",
        json={"email": "security-audit-safety@example.com", "password": TEST_ONLY_PASSWORD},
    )

    combined = " ".join(str(entry.changes) for entry in audit_entries(db_session))

    assert login.json()["access_token"] not in combined
    assert login.json()["refresh_token"] not in combined


def test_no_legacy_security_control_module_paths_exist() -> None:
    project_root = Path(__file__).resolve().parents[1]

    assert not (project_root / "app" / "security_headers.py").exists()
    assert not (project_root / "app" / "rate_limit.py").exists()

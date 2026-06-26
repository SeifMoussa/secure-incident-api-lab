from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_audit_api_never_exposes_sensitive_auth_material(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-sensitive-admin@example.com")
    login = client.post(
        "/auth/login",
        json={"email": admin.email, "password": TEST_ONLY_PASSWORD},
    )
    assert login.status_code == 200
    tokens = login.json()
    create_incident_via_api(client, test_settings, admin)

    response = client.get("/audit/", headers=bearer_header(test_settings, admin))

    assert response.status_code == 200
    text = response.text
    forbidden = [
        TEST_ONLY_PASSWORD,
        tokens["access_token"],
        tokens["refresh_token"],
        "password_hash",
        "Authorization",
        "api_key",
        "jwt_secret",
        "secret-for-phase",
    ]
    assert all(value not in text for value in forbidden)


def test_phase_7_did_not_add_rate_limit_security_headers_or_ci_files() -> None:
    from pathlib import Path

    project_root = Path(__file__).resolve().parents[1]
    forbidden_paths = [
        project_root / "app" / "security_headers.py",
        project_root / "app" / "rate_limit.py",
        project_root / "app" / "cors.py",
    ]
    assert all(not path.exists() for path in forbidden_paths)

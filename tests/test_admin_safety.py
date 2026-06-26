from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def test_admin_responses_do_not_include_sensitive_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="safety-admin@example.com", role=Role.ADMIN)

    list_response = client.get("/admin/users/", headers=bearer_header(test_settings, admin))
    detail_response = client.get(
        f"/admin/users/{admin.user_id}",
        headers=bearer_header(test_settings, admin),
    )
    combined_text = list_response.text + detail_response.text

    assert "password_hash" not in combined_text
    assert "access_token" not in combined_text
    assert "refresh_token" not in combined_text
    assert test_settings.jwt_secret_key not in combined_text


def test_no_legacy_routes_phase8_ci_or_git_files_started() -> None:
    root = Path(__file__).resolve().parents[1]
    forbidden_paths = [
        "app/api/routes/incidents.py",
        "app/api/routes/tickets.py",
        "app/api/routes/evidence.py",
        "app/api/routes/remediation.py",
        "app/api/routes/audit.py",
        "app/security_headers.py",
        "app/rate_limit.py",
        ".git/HEAD",
    ]

    for relative_path in forbidden_paths:
        assert not (root / relative_path).exists(), relative_path

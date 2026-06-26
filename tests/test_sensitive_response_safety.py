from collections.abc import Iterable

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_rate_limiting import client_with_settings

FORBIDDEN_FRAGMENTS = [
    "password_hash",
    TEST_ONLY_PASSWORD,
    "jwt_secret",
    "authorization:",
    "bearer ",
    "api_key",
    "traceback",
    "sqlalchemy",
    "integrityerror",
    "valueerror",
]


def assert_safe_response_text(responses: Iterable) -> None:
    combined = "\n".join(response.text.lower() for response in responses)
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment.lower() not in combined


def test_error_responses_do_not_expose_sensitive_or_internal_details(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="safe-errors-admin@example.com", role=Role.ADMIN
    )
    viewer = create_synthetic_user(
        db_session, email="safe-errors-viewer@example.com", role=Role.VIEWER
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    admin_headers = bearer_header(test_settings, admin)
    viewer_headers = bearer_header(test_settings, viewer)

    responses = [
        client.post(
            "/auth/login",
            json={"email": admin.email, "password": "SyntheticWrong!123"},
        ),
        client.get("/admin/users/not-real", headers=admin_headers),
        client.post(
            "/incidents/",
            json={"title": "bad"},
            headers=viewer_headers,
        ),
        client.get(f"/incidents/{incident.incident_id}/tickets/not-real", headers=admin_headers),
        client.get(f"/incidents/{incident.incident_id}/evidence/not-real", headers=admin_headers),
        client.patch(
            f"/incidents/{incident.incident_id}/remediation/not-real",
            json={"status": "COMPLETE"},
            headers=admin_headers,
        ),
        client.get("/audit/", headers=viewer_headers),
        client.post("/auth/register", json={"email": "not-an-email", "password_hash": "x"}),
    ]

    assert {401, 403, 404, 422}.issubset({response.status_code for response in responses})
    assert_safe_response_text(responses)


def test_rate_limit_error_response_is_sensitive_safe(db_session: Session) -> None:
    settings = Settings(
        environment="test",
        jwt_secret_key="synthetic-rate-limit-secret",
        rate_limit_enabled=True,
        rate_limit_default_per_minute=1,
    )
    with client_with_settings(settings, db_session) as client:
        client.get("/health")
        response = client.get("/health")

    assert response.status_code == 429
    assert_safe_response_text([response])


def test_non_auth_responses_do_not_expose_tokens(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="safe-token-admin@example.com", role=Role.ADMIN)
    response = client.get("/auth/me", headers=bearer_header(test_settings, admin))

    assert response.status_code == 200
    assert "access_token" not in response.text
    assert "refresh_token" not in response.text

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from app.main import create_app
from tests.auth_test_helpers import (
    TEST_ONLY_PASSWORD,
    bearer_header,
    create_synthetic_user,
)

REQUIRED_HEADERS = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "x-xss-protection": "1; mode=block",
    "referrer-policy": "no-referrer",
    "cache-control": "no-store",
    "content-security-policy": "default-src 'none'",
}


def test_security_headers_appear_on_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    for header, value in REQUIRED_HEADERS.items():
        assert response.headers[header] == value


def test_security_headers_appear_on_auth_response(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "security-headers-auth@example.com",
            "password": TEST_ONLY_PASSWORD,
            "display_name": "Synthetic Security Header User",
        },
    )

    assert response.status_code == 201
    for header, value in REQUIRED_HEADERS.items():
        assert response.headers[header] == value


def test_security_headers_appear_on_protected_error_response(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    for header, value in REQUIRED_HEADERS.items():
        assert response.headers[header] == value


def test_security_headers_do_not_expose_secrets(client: TestClient) -> None:
    response = client.get("/health")
    combined_headers = " ".join(f"{key}: {value}" for key, value in response.headers.items())

    forbidden = ["password", "password_hash", "access_token", "refresh_token", "api_key", "secret"]
    assert all(value not in combined_headers.lower() for value in forbidden)


def test_production_hsts_header_exists() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="synthetic-production-secret-for-tests-only",
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app, base_url="https://testserver") as client:
        response = client.get("/health")

    assert response.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"


def test_docs_are_not_broken_when_enabled_in_test() -> None:
    settings = Settings(
        environment="test",
        debug=True,
        jwt_secret_key="synthetic-test-secret-for-docs-only",
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app) as client:
        response = client.get("/docs")

    assert response.status_code == 200
    assert "content-security-policy" not in response.headers


def test_security_headers_on_forbidden_response(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    viewer = create_synthetic_user(db_session, email="headers-viewer@example.com", role=Role.VIEWER)

    response = client.post(
        "/incidents/",
        json={
            "title": "Synthetic forbidden security header incident",
            "description": "Synthetic test-only incident.",
            "severity": "LOW",
            "status": "OPEN",
        },
        headers=bearer_header(test_settings, viewer),
    )

    assert response.status_code == 403
    assert response.headers["x-content-type-options"] == "nosniff"

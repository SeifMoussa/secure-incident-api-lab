from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_allowed_localhost_origin_gets_cors_headers(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_disallowed_origin_is_not_allowed(client: TestClient) -> None:
    response = client.options(
        "/health",
        headers={
            "Origin": "https://disallowed.example.test",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_wildcard_is_not_enabled_by_default(test_settings: Settings) -> None:
    assert "*" not in test_settings.effective_cors_allowed_origins


def test_production_cors_defaults_to_safe_empty_allowlist() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="synthetic-production-secret-for-cors-only",
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app, base_url="https://testserver") as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert settings.effective_cors_allowed_origins == []
    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_production_cors_uses_explicit_allowlist() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="synthetic-production-secret-for-cors-only",
        cors_allowed_origins=["https://app.example.test"],
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app, base_url="https://testserver") as client:
        response = client.options(
            "/health",
            headers={
                "Origin": "https://app.example.test",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://app.example.test"

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_create_app_returns_fastapi_application(test_settings: Settings) -> None:
    app = create_app(test_settings)

    assert app.title == "Secure Incident Management API"
    assert app.version == "0.1.0"
    assert app.state.settings is test_settings


def test_health_endpoint_returns_200(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200


def test_health_response_shape(client: TestClient) -> None:
    response = client.get("/health")

    assert response.json() == {
        "status": "ok",
        "service": "Secure Incident Management API",
        "version": "0.1.0",
        "environment": "test",
        "docs_enabled": True,
    }


def test_root_endpoint_returns_safe_message(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "service": "Secure Incident Management API",
        "message": "Secure Incident Management API scaffold is running.",
    }
    assert "secret" not in response.text.lower()
    assert "token" not in response.text.lower()


def test_docs_enabled_in_test_environment(test_settings: Settings) -> None:
    app = create_app(test_settings)

    assert app.docs_url == "/docs"
    assert app.openapi_url == "/openapi.json"


def test_docs_disabled_in_production_environment() -> None:
    app = create_app(
        Settings(
            environment="production",
            jwt_secret_key="local-test-value-that-is-not-used-as-a-real-secret",  # noqa: S106
        )
    )

    assert app.docs_url is None
    assert app.redoc_url is None
    assert app.openapi_url is None

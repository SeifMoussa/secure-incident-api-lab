import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.config import LOCAL_SECRET_PLACEHOLDER, Settings
from app.main import create_app


def test_docs_disabled_in_production() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="synthetic-production-secret-for-docs-only",
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app, base_url="https://testserver") as client:
        response = client.get("/docs")

    assert response.status_code == 404


def test_https_redirect_enabled_in_production() -> None:
    settings = Settings(
        environment="production",
        jwt_secret_key="synthetic-production-secret-for-redirect-only",
        rate_limit_enabled=False,
    )
    app = create_app(settings)

    with TestClient(app, follow_redirects=False) as client:
        response = client.get("/health")

    assert response.status_code in {307, 308}
    assert response.headers["location"].startswith("https://")


def test_production_placeholder_jwt_secret_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret_key=LOCAL_SECRET_PLACEHOLDER)


def test_test_and_development_https_redirect_disabled() -> None:
    for environment in ["test", "development"]:
        settings = Settings(
            environment=environment,
            jwt_secret_key=f"synthetic-{environment}-secret-for-redirect-only",
            rate_limit_enabled=False,
        )
        app = create_app(settings)

        with TestClient(app, follow_redirects=False) as client:
            response = client.get("/health")

        assert response.status_code == 200

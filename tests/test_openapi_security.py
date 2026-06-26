from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_openapi_contains_bearer_security_and_expected_endpoints(client: TestClient) -> None:
    schema = client.get("/openapi.json").json()

    assert "HTTPBearer" in schema["components"]["securitySchemes"]
    for path in [
        "/auth/register",
        "/auth/login",
        "/admin/users/",
        "/incidents/",
        "/incidents/{incident_id}/tickets/",
        "/incidents/{incident_id}/evidence/",
        "/incidents/{incident_id}/remediation/",
        "/audit/",
    ]:
        assert path in schema["paths"]
    assert schema["paths"]["/admin/users/"]["get"]["security"] == [{"HTTPBearer": []}]
    assert schema["paths"]["/audit/"]["get"]["security"] == [{"HTTPBearer": []}]


def test_openapi_does_not_expose_password_hash_or_secret_settings(client: TestClient) -> None:
    schema_text = client.get("/openapi.json").text.lower()

    assert "password_hash" not in schema_text
    assert "jwt_secret" not in schema_text
    assert "api_key" not in schema_text


def test_docs_and_openapi_environment_visibility() -> None:
    test_app = create_app(
        Settings(
            environment="test",
            jwt_secret_key="synthetic-openapi-test-secret",
            rate_limit_enabled=False,
        )
    )
    production_app = create_app(
        Settings(
            environment="production",
            jwt_secret_key="synthetic-openapi-production-secret",
            rate_limit_enabled=False,
        )
    )

    with TestClient(test_app) as client:
        assert client.get("/docs").status_code == 200
        assert client.get("/openapi.json").status_code == 200
    with TestClient(production_app, base_url="https://testserver") as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404

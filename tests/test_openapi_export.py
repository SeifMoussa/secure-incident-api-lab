import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app
from scripts.export_openapi import export_openapi

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_JSON = ROOT / "docs" / "openapi.json"


def test_openapi_export_script_writes_schema() -> None:
    output_path = export_openapi()

    assert output_path == Path("docs") / "openapi.json"
    assert OPENAPI_JSON.is_file()
    schema = json.loads(OPENAPI_JSON.read_text(encoding="utf-8"))
    assert schema["info"]["title"] == "Secure Incident Management API"
    assert "HTTPBearer" in schema["components"]["securitySchemes"]


def test_openapi_export_matches_app_factory_paths() -> None:
    exported = json.loads(OPENAPI_JSON.read_text(encoding="utf-8"))
    app_schema = create_app(Settings(environment="test", rate_limit_enabled=False)).openapi()

    assert exported["paths"].keys() == app_schema["paths"].keys()
    assert exported["components"]["securitySchemes"] == app_schema["components"]["securitySchemes"]


def test_openapi_schema_is_safe_and_production_docs_remain_disabled() -> None:
    schema_text = OPENAPI_JSON.read_text(encoding="utf-8").lower()

    assert "password_hash" not in schema_text
    assert "jwt_secret" not in schema_text
    assert "api_key" not in schema_text

    production_app = create_app(
        Settings(
            environment="production",
            jwt_secret_key="synthetic-production-openapi-docs-secret",
            rate_limit_enabled=False,
        )
    )
    with TestClient(production_app, base_url="https://testserver") as client:
        assert client.get("/docs").status_code == 404
        assert client.get("/openapi.json").status_code == 404

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_REFERENCE = ROOT / "docs" / "api_reference.md"

IMPLEMENTED_ENDPOINTS = [
    "GET /",
    "GET /health",
    "POST /auth/register",
    "POST /auth/login",
    "POST /auth/refresh",
    "POST /auth/logout",
    "GET /auth/me",
    "GET /admin/users/",
    "GET /admin/users/{uid}",
    "PATCH /admin/users/{uid}/role",
    "DELETE /admin/users/{uid}",
    "POST /incidents/",
    "GET /incidents/",
    "GET /incidents/{incident_id}",
    "PATCH /incidents/{incident_id}",
    "DELETE /incidents/{incident_id}",
    "GET /incidents/{incident_id}/timeline",
    "POST /incidents/{incident_id}/tickets/",
    "GET /incidents/{incident_id}/tickets/",
    "GET /incidents/{incident_id}/tickets/{ticket_id}",
    "PATCH /incidents/{incident_id}/tickets/{ticket_id}",
    "DELETE /incidents/{incident_id}/tickets/{ticket_id}",
    "POST /incidents/{incident_id}/evidence/",
    "GET /incidents/{incident_id}/evidence/",
    "GET /incidents/{incident_id}/evidence/{evidence_id}",
    "PATCH /incidents/{incident_id}/evidence/{evidence_id}",
    "DELETE /incidents/{incident_id}/evidence/{evidence_id}",
    "POST /incidents/{incident_id}/remediation/",
    "GET /incidents/{incident_id}/remediation/",
    "PATCH /incidents/{incident_id}/remediation/{task_id}",
    "DELETE /incidents/{incident_id}/remediation/{task_id}",
    "GET /audit/",
]


def test_api_reference_exists_and_documents_all_implemented_endpoints() -> None:
    text = API_REFERENCE.read_text(encoding="utf-8")

    assert API_REFERENCE.is_file()
    for endpoint in IMPLEMENTED_ENDPOINTS:
        assert f"### {endpoint}" in text


def test_api_reference_documents_security_and_roles() -> None:
    text = API_REFERENCE.read_text(encoding="utf-8").lower()

    for phrase in [
        "authentication requirement",
        "allowed roles",
        "audit behavior",
        "admin",
        "analyst",
        "viewer",
        "auditor",
        "metadata only",
        "no binary upload",
        "server-managed fields are rejected",
    ]:
        assert phrase in text


def test_api_reference_does_not_claim_unimplemented_routes_complete() -> None:
    text = API_REFERENCE.read_text(encoding="utf-8")

    for route in [
        "POST /audit/",
        "PATCH /audit/",
        "DELETE /audit/",
        "POST /incidents/{incident_id}/attachments",
        "GET /users",
        "PATCH /users/{user_id}/deactivate",
    ]:
        assert f"### {route}" not in text

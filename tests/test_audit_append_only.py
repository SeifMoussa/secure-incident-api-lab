from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import Settings
from tests.auth_test_helpers import bearer_header
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_audit_log_is_append_only_at_api_level(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-append-admin@example.com")
    create_incident_via_api(client, test_settings, admin)
    headers = bearer_header(test_settings, admin)

    post_response = client.post("/audit/", json={}, headers=headers)
    patch_response = client.patch("/audit/synthetic-id", json={}, headers=headers)
    delete_response = client.delete("/audit/synthetic-id", headers=headers)

    assert post_response.status_code in {404, 405}
    assert patch_response.status_code in {404, 405}
    assert delete_response.status_code in {404, 405}

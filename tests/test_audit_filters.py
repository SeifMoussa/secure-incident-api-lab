from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import AuditAction, AuditOutcome
from app.config import Settings
from tests.auth_test_helpers import bearer_header
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_audit_filters_work_independently(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-filter-split-admin@example.com")
    first = create_incident_via_api(client, test_settings, admin, title="Synthetic first filter")
    second = create_incident_via_api(client, test_settings, admin, title="Synthetic second filter")
    headers = bearer_header(test_settings, admin)

    client.patch(
        f"/incidents/{first['incident_id']}",
        json={"status": "CONTAINED"},
        headers=headers,
    )

    assert client.get("/audit/?resource_type=incident", headers=headers).json()["total"] == 3
    assert (
        client.get(f"/audit/?resource_id={second['incident_id']}", headers=headers).json()["total"]
        == 1
    )
    assert client.get(f"/audit/?actor={admin.user_id}", headers=headers).json()["total"] == 3
    assert client.get(f"/audit/?action={AuditAction.UPDATE}", headers=headers).json()["total"] == 1
    assert (
        client.get(f"/audit/?outcome={AuditOutcome.SUCCESS}", headers=headers).json()["total"] == 3
    )


def test_audit_pagination_and_newest_first_ordering(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-pagination-admin@example.com")
    incident = create_incident_via_api(client, test_settings, admin)
    headers = bearer_header(test_settings, admin)
    client.patch(
        f"/incidents/{incident['incident_id']}",
        json={"status": "CONTAINED"},
        headers=headers,
    )
    client.delete(f"/incidents/{incident['incident_id']}", headers=headers)

    response = client.get("/audit/?page=1&page_size=2", headers=headers)

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] == 3
    assert [item["action"] for item in body["items"]] == ["DELETE", "UPDATE"]

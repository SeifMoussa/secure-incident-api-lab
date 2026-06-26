from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import AuditAction, AuditOutcome, Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.test_audit_helpers import create_admin, create_incident_via_api


def test_admin_and_auditor_can_read_audit_log(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-read-admin@example.com")
    auditor = create_synthetic_user(db_session, email="audit-reader@example.com", role=Role.AUDITOR)
    create_incident_via_api(client, test_settings, admin)

    assert client.get("/audit/", headers=bearer_header(test_settings, admin)).status_code == 200
    assert client.get("/audit/", headers=bearer_header(test_settings, auditor)).status_code == 200


def test_non_audit_roles_and_missing_token_cannot_read_audit_log(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-deny-admin@example.com")
    create_incident_via_api(client, test_settings, admin)

    for role in [Role.ANALYST, Role.VIEWER]:
        user = create_synthetic_user(
            db_session, email=f"audit-deny-{role.value.lower()}@example.com", role=role
        )
        assert client.get("/audit/", headers=bearer_header(test_settings, user)).status_code == 403
    assert client.get("/audit/").status_code == 401


def test_audit_read_filters_pagination_and_newest_first_ordering(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-filter-admin@example.com")
    incident_one = create_incident_via_api(
        client, test_settings, admin, title="Synthetic filter incident one"
    )
    incident_two = create_incident_via_api(
        client, test_settings, admin, title="Synthetic filter incident two"
    )
    headers = bearer_header(test_settings, admin)
    client.patch(
        f"/incidents/{incident_one['incident_id']}",
        json={"status": "CONTAINED"},
        headers=headers,
    )

    response = client.get("/audit/?page=1&page_size=2", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["items"][0]["action"] == AuditAction.UPDATE

    assert client.get("/audit/?resource_type=incident", headers=headers).json()["total"] == 3
    assert (
        client.get(f"/audit/?resource_id={incident_two['incident_id']}", headers=headers).json()[
            "total"
        ]
        == 1
    )
    assert client.get(f"/audit/?actor={admin.user_id}", headers=headers).json()["total"] == 3
    assert client.get("/audit/?action=UPDATE", headers=headers).json()["total"] == 1
    assert client.get("/audit/?outcome=SUCCESS", headers=headers).json()["total"] == 3


def test_audit_response_is_sanitized(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-safety-admin@example.com")
    create_incident_via_api(client, test_settings, admin)

    response = client.get("/audit/", headers=bearer_header(test_settings, admin))

    forbidden = [
        "password_hash",
        "SyntheticPhase",
        "access_token",
        "refresh_token",
        "Authorization",
        "api_key",
        "jwt_secret",
    ]
    text = response.text
    assert all(value not in text for value in forbidden)


def test_audit_filter_enums_reject_invalid_values(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_admin(db_session, "audit-invalid-filter-admin@example.com")

    invalid_action = client.get(
        "/audit/?action=INVALID", headers=bearer_header(test_settings, admin)
    )
    invalid_outcome = client.get(
        "/audit/?outcome=UNKNOWN", headers=bearer_header(test_settings, admin)
    )
    assert invalid_action.status_code == 422
    assert invalid_outcome.status_code == 422


def test_audit_outcome_failure_filter(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    viewer = create_synthetic_user(
        db_session, email="audit-failure-filter-viewer@example.com", role=Role.VIEWER
    )
    admin = create_admin(db_session, "audit-failure-filter-admin@example.com")
    client.post(
        "/incidents/",
        json={
            "title": "Blocked synthetic incident",
            "description": "Synthetic incident that should be forbidden.",
            "severity": "LOW",
            "status": "OPEN",
        },
        headers=bearer_header(test_settings, viewer),
    )

    response = client.get(
        f"/audit/?outcome={AuditOutcome.FAILURE}",
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1

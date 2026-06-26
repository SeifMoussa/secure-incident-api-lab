from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def test_pagination_rejects_invalid_page_and_page_size(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="pagination-admin@example.com", role=Role.ADMIN)
    headers = bearer_header(test_settings, admin)

    for query in ["page=0", "page_size=0", "page_size=101"]:
        response = client.get(f"/incidents/?{query}", headers=headers)
        assert response.status_code == 422


def test_incident_filters_reject_invalid_enums_uuid_and_datetime(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="filter-validation-admin@example.com", role=Role.ADMIN
    )
    headers = bearer_header(test_settings, admin)

    for query in [
        "severity=SEVERE",
        "status=UNKNOWN",
        "assigned_to=not-a-uuid",
        "created_after=not-a-date",
        "created_before=not-a-date",
    ]:
        response = client.get(f"/incidents/?{query}", headers=headers)
        assert response.status_code == 422


def test_tag_filter_is_safe_and_pagination_metadata_is_consistent(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="filter-tag-admin@example.com", role=Role.ADMIN)
    headers = bearer_header(test_settings, admin)

    response = client.get(
        "/incidents/?tag=missing-synthetic-tag&page=1&page_size=5", headers=headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["page"] == 1
    assert body["page_size"] == 5
    assert body["total"] == 0

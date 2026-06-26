from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import IncidentSeverity, Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def test_list_incidents_works_for_all_roles(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    creator = create_synthetic_user(db_session, email="list-creator@example.com", role=Role.ADMIN)
    create_synthetic_incident(db_session, created_by=creator.user_id)

    for role in [Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session,
            email=f"list-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.get("/incidents/", headers=bearer_header(test_settings, user))

        assert response.status_code == 200
        assert response.json()["total"] == 1


def test_list_pagination_defaults_and_max_page_size(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="list-admin@example.com", role=Role.ADMIN)

    default_response = client.get("/incidents/", headers=bearer_header(test_settings, admin))
    too_large_response = client.get(
        "/incidents/?page_size=101",
        headers=bearer_header(test_settings, admin),
    )

    assert default_response.status_code == 200
    assert default_response.json()["page"] == 1
    assert default_response.json()["page_size"] == 20
    assert too_large_response.status_code == 422


def test_soft_deleted_incidents_are_excluded_from_list(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="deleted-list-admin@example.com", role=Role.ADMIN
    )
    visible = create_synthetic_incident(
        db_session,
        created_by=admin.user_id,
        title="Visible synthetic incident",
    )
    deleted = create_synthetic_incident(
        db_session,
        created_by=admin.user_id,
        title="Deleted synthetic incident",
        severity=IncidentSeverity.LOW,
    )
    deleted.is_deleted = True
    db_session.commit()

    response = client.get("/incidents/", headers=bearer_header(test_settings, admin))

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["items"][0]["incident_id"] == visible.incident_id

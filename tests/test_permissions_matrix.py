from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def test_phase_4_admin_user_management_permission_matrix(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    expected_status = {
        Role.ADMIN: 200,
        Role.ANALYST: 403,
        Role.VIEWER: 403,
        Role.AUDITOR: 403,
    }

    for role, status_code in expected_status.items():
        user = create_synthetic_user(
            db_session,
            email=f"matrix-{role.value.lower()}@example.com",
            role=role,
        )
        response = client.get("/admin/users/", headers=bearer_header(test_settings, user))

        assert response.status_code == status_code

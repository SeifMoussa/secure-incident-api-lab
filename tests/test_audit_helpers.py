from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.auth.models import User
from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user


def create_admin(db_session: Session, email: str = "audit-admin@example.com") -> User:
    return create_synthetic_user(db_session, email=email, role=Role.ADMIN)


def admin_headers(settings: Settings, admin: User) -> dict[str, str]:
    return bearer_header(settings, admin)


def audit_entries(db_session: Session) -> list[AuditLog]:
    return db_session.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()


def create_incident_via_api(
    client: TestClient,
    settings: Settings,
    admin: User,
    *,
    title: str = "Synthetic audited incident",
) -> dict[str, object]:
    response = client.post(
        "/incidents/",
        json={
            "title": title,
            "description": "Synthetic defensive incident for audit tests.",
            "severity": "HIGH",
            "status": "OPEN",
            "tags": ["audit"],
        },
        headers=admin_headers(settings, admin),
    )
    assert response.status_code == 201
    return response.json()

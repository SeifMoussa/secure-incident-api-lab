from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.test_incidents_create import valid_payload


def test_incident_validation_rejects_invalid_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="validation-admin@example.com", role=Role.ADMIN)
    header = bearer_header(test_settings, admin)

    cases = [
        valid_payload(severity="SEVERE"),
        valid_payload(status="UNKNOWN"),
        valid_payload(title="bad"),
        valid_payload(description="x" * 5001),
        valid_payload(mitre_tactic="unsafe-tactic"),
        valid_payload(mitre_technique="TA0001"),
        valid_payload(tags=[f"tag-{number}" for number in range(11)]),
        valid_payload(tags=["x" * 51]),
        valid_payload(assigned_to="not-a-uuid"),
    ]

    for payload in cases:
        response = client.post("/incidents/", json=payload, headers=header)

        assert response.status_code == 422


def test_incident_validation_accepts_safe_mitre_fields(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="mitre-admin@example.com", role=Role.ADMIN)

    response = client.post(
        "/incidents/",
        json=valid_payload(mitre_tactic="initial-access", mitre_technique="T1110.001"),
        headers=bearer_header(test_settings, admin),
    )

    assert response.status_code == 201
    assert response.json()["mitre_tactic"] == "initial-access"
    assert response.json()["mitre_technique"] == "T1110.001"

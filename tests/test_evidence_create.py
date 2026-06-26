from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident


def evidence_payload(**overrides):
    payload = {
        "content": "## Synthetic evidence note",
        "source": "synthetic-source",
        "collected_at": datetime.now(UTC).isoformat(),
        "tags": ["Synthetic"],
        "attachments": [
            {
                "filename": "synthetic-note.txt",
                "content_type": "text/plain",
                "size_bytes": 42,
                "storage_reference": "metadata-only-reference",
            }
        ],
    }
    payload.update(overrides)
    return payload


def test_evidence_create_with_metadata_attachment(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="evidence-create-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    response = client.post(
        f"/incidents/{incident.incident_id}/evidence/",
        json=evidence_payload(),
        headers=bearer_header(test_settings, admin),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["created_by"] == admin.user_id
    assert body["attachments"][0]["filename"] == "synthetic-note.txt"
    assert "file_bytes" not in response.text


def test_evidence_create_rbac_and_validation(
    client: TestClient, db_session: Session, test_settings: Settings
) -> None:
    admin = create_synthetic_user(
        db_session, email="evidence-rbac-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    for role in [Role.VIEWER, Role.AUDITOR]:
        user = create_synthetic_user(
            db_session, email=f"evidence-deny-{role.value.lower()}@example.com", role=role
        )
        assert (
            client.post(
                f"/incidents/{incident.incident_id}/evidence/",
                json=evidence_payload(),
                headers=bearer_header(test_settings, user),
            ).status_code
            == 403
        )
    cases = [
        evidence_payload(content="x" * 10001),
        evidence_payload(source=""),
        evidence_payload(tags=["x" * 51]),
        evidence_payload(
            attachments=[
                {
                    "filename": "bad/path.txt",
                    "content_type": "text/plain",
                    "size_bytes": 1,
                    "storage_reference": "ref",
                }
            ]
        ),
        evidence_payload(
            attachments=[
                {
                    "filename": "ok.txt",
                    "content_type": "text/plain",
                    "size_bytes": -1,
                    "storage_reference": "ref",
                }
            ]
        ),
        evidence_payload(file_path="C:/real/file.txt"),
    ]
    for payload in cases:
        response = client.post(
            f"/incidents/{incident.incident_id}/evidence/",
            json=payload,
            headers=bearer_header(test_settings, admin),
        )
        assert response.status_code == 422

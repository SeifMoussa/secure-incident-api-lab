from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings
from tests.auth_test_helpers import bearer_header, create_synthetic_user
from tests.incident_test_helpers import create_synthetic_incident
from tests.test_evidence_create import evidence_payload


def test_incident_mitre_tag_and_uuid_validation(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(db_session, email="validation-admin@example.com", role=Role.ADMIN)
    headers = bearer_header(test_settings, admin)

    for payload in [
        {
            "title": "Synthetic invalid tactic",
            "description": "Synthetic defensive test.",
            "severity": "LOW",
            "mitre_tactic": "invalid-tactic",
        },
        {
            "title": "Synthetic invalid technique",
            "description": "Synthetic defensive test.",
            "severity": "LOW",
            "mitre_technique": "TA0001",
        },
        {
            "title": "Synthetic invalid assigned user",
            "description": "Synthetic defensive test.",
            "severity": "LOW",
            "assigned_to": "not-a-uuid",
        },
        {
            "title": "Synthetic invalid tags",
            "description": "Synthetic defensive test.",
            "severity": "LOW",
            "tags": ["x" * 51],
        },
    ]:
        response = client.post("/incidents/", json=payload, headers=headers)
        assert response.status_code == 422


def test_evidence_attachment_metadata_validation_regressions(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    admin = create_synthetic_user(
        db_session, email="validation-evidence-admin@example.com", role=Role.ADMIN
    )
    incident = create_synthetic_incident(db_session, created_by=admin.user_id)
    headers = bearer_header(test_settings, admin)

    for attachment in [
        {
            "filename": "../synthetic.txt",
            "content_type": "text/plain",
            "size_bytes": 1,
            "storage_reference": "metadata-only",
        },
        {
            "filename": "synthetic.txt",
            "content_type": "not-a-content-type",
            "size_bytes": 1,
            "storage_reference": "metadata-only",
        },
        {
            "filename": "synthetic.txt",
            "content_type": "text/plain",
            "size_bytes": -1,
            "storage_reference": "metadata-only",
        },
    ]:
        response = client.post(
            f"/incidents/{incident.incident_id}/evidence/",
            json=evidence_payload(attachments=[attachment]),
            headers=headers,
        )
        assert response.status_code == 422

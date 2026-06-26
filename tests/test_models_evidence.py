from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import IncidentSeverity, IncidentStatus
from app.evidence.models import EvidenceAttachment, EvidenceNote
from app.incidents.models import Incident


def test_evidence_note_model_fields_exist() -> None:
    columns = set(EvidenceNote.__table__.columns.keys())

    assert {
        "evidence_id",
        "incident_id",
        "content",
        "source",
        "collected_at",
        "created_by",
        "tags",
        "is_deleted",
        "created_at",
        "updated_at",
    } <= columns


def test_evidence_attachment_is_metadata_only() -> None:
    columns = set(EvidenceAttachment.__table__.columns.keys())

    assert {
        "attachment_id",
        "evidence_id",
        "filename",
        "content_type",
        "size_bytes",
        "storage_reference",
        "created_at",
    } <= columns
    assert "blob" not in columns
    assert "binary" not in columns
    assert "file_bytes" not in columns


def test_evidence_json_tags_and_attachment_relationship(db_session: Session) -> None:
    user = User(
        email="evidence-user@example.com",
        display_name="Synthetic Evidence User",
        password_hash="synthetic-hash-only",
    )
    db_session.add(user)
    db_session.flush()
    incident = Incident(
        title="Synthetic incident",
        description="Synthetic defensive incident record.",
        severity=IncidentSeverity.LOW,
        status=IncidentStatus.OPEN,
        created_by=user.user_id,
    )
    db_session.add(incident)
    db_session.flush()
    note = EvidenceNote(
        incident_id=incident.incident_id,
        content="## Synthetic markdown evidence",
        source="synthetic-source",
        collected_at=datetime.now(UTC),
        created_by=user.user_id,
        tags=["note", "metadata-only"],
    )
    db_session.add(note)
    db_session.flush()
    attachment = EvidenceAttachment(
        evidence_id=note.evidence_id,
        filename="synthetic-note.txt",
        content_type="text/plain",
        size_bytes=128,
        storage_reference="metadata-only-reference",
    )
    db_session.add(attachment)
    db_session.commit()
    db_session.refresh(note)

    assert note.tags == ["note", "metadata-only"]
    assert note.is_deleted is False
    assert note.attachments[0].filename == "synthetic-note.txt"

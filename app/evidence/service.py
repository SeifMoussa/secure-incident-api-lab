"""Evidence note service-layer operations."""

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import Role
from app.common.models import utc_now
from app.common.pagination import PaginationParams
from app.evidence.models import EvidenceAttachment, EvidenceNote
from app.evidence.schemas import (
    EvidenceAttachmentRequest,
    EvidenceAttachmentResponse,
    EvidenceCreateRequest,
    EvidenceDeleteResponse,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceUpdateRequest,
)
from app.incidents.models import Incident


class EvidenceServiceError(ValueError):
    """Raised for expected safe evidence workflow failures."""


def create_evidence(
    db: Session,
    *,
    incident_id: str,
    actor: User,
    payload: EvidenceCreateRequest,
) -> EvidenceResponse:
    _get_active_incident_or_raise(db, incident_id)
    note = EvidenceNote(
        incident_id=incident_id,
        content=payload.content,
        source=payload.source,
        collected_at=payload.collected_at,
        created_by=actor.user_id,
        tags=payload.tags,
    )
    db.add(note)
    db.flush()
    _replace_attachments(db, note.evidence_id, payload.attachments)
    db.commit()
    db.refresh(note)
    return evidence_response(note)


def list_evidence(
    db: Session, *, incident_id: str, pagination: PaginationParams
) -> EvidenceListResponse:
    _get_active_incident_or_raise(db, incident_id)
    query = select(EvidenceNote).where(
        EvidenceNote.incident_id == incident_id,
        EvidenceNote.is_deleted.is_(False),
    )
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    notes = db.scalars(
        query.order_by(EvidenceNote.created_at.desc(), EvidenceNote.source.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return EvidenceListResponse(
        items=[evidence_response(note) for note in notes],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def get_evidence(db: Session, *, incident_id: str, evidence_id: str) -> EvidenceResponse:
    return evidence_response(_get_active_evidence_or_raise(db, incident_id, evidence_id))


def update_evidence(
    db: Session,
    *,
    incident_id: str,
    evidence_id: str,
    actor: User,
    payload: EvidenceUpdateRequest,
) -> EvidenceResponse:
    note = _get_active_evidence_or_raise(db, incident_id, evidence_id)
    if actor.role == Role.ANALYST and note.created_by != actor.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions."
        )
    data = payload.model_dump(exclude_unset=True)
    attachments = data.pop("attachments", None)
    for field_name, value in data.items():
        setattr(note, field_name, value)
    if attachments is not None:
        _replace_attachments(db, note.evidence_id, attachments)
    note.updated_at = utc_now()
    db.commit()
    db.refresh(note)
    return evidence_response(note)


def soft_delete_evidence(
    db: Session, *, incident_id: str, evidence_id: str
) -> EvidenceDeleteResponse:
    note = _get_active_evidence_or_raise(db, incident_id, evidence_id)
    note.is_deleted = True
    note.updated_at = utc_now()
    db.commit()
    db.refresh(note)
    return EvidenceDeleteResponse(
        message="Evidence note deleted.", evidence=evidence_response(note)
    )


def evidence_response(note: EvidenceNote) -> EvidenceResponse:
    return EvidenceResponse(
        evidence_id=note.evidence_id,
        incident_id=note.incident_id,
        content=note.content,
        source=note.source,
        collected_at=note.collected_at.isoformat(),
        created_by=note.created_by,
        tags=note.tags,
        is_deleted=note.is_deleted,
        created_at=note.created_at.isoformat(),
        updated_at=note.updated_at.isoformat(),
        attachments=[attachment_response(attachment) for attachment in note.attachments],
    )


def attachment_response(attachment: EvidenceAttachment) -> EvidenceAttachmentResponse:
    return EvidenceAttachmentResponse(
        attachment_id=attachment.attachment_id,
        filename=attachment.filename,
        content_type=attachment.content_type,
        size_bytes=attachment.size_bytes,
        storage_reference=attachment.storage_reference,
        created_at=attachment.created_at.isoformat(),
    )


def _replace_attachments(
    db: Session,
    evidence_id: str,
    attachments: list[EvidenceAttachmentRequest],
) -> None:
    db.execute(delete(EvidenceAttachment).where(EvidenceAttachment.evidence_id == evidence_id))
    for attachment in attachments:
        db.add(EvidenceAttachment(evidence_id=evidence_id, **attachment.model_dump()))


def _get_active_incident_or_raise(db: Session, incident_id: str) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None or incident.is_deleted:
        msg = "Incident not found."
        raise EvidenceServiceError(msg)
    return incident


def _get_active_evidence_or_raise(db: Session, incident_id: str, evidence_id: str) -> EvidenceNote:
    _get_active_incident_or_raise(db, incident_id)
    note = db.get(EvidenceNote, evidence_id)
    if note is None or note.is_deleted or note.incident_id != incident_id:
        msg = "Evidence note not found."
        raise EvidenceServiceError(msg)
    return note

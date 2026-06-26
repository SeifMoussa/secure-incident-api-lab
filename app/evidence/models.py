"""Evidence note and attachment metadata ORM models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.models import TimestampMixin, utc_now
from app.common.types import new_uuid, uuid_string
from app.database import Base

if TYPE_CHECKING:
    from app.incidents.models import Incident


class EvidenceNote(TimestampMixin, Base):
    """Markdown evidence note for a synthetic incident."""

    __tablename__ = "evidence_notes"

    evidence_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source: Mapped[str] = mapped_column(String(200), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    incident: Mapped["Incident"] = relationship(back_populates="evidence_notes")
    attachments: Mapped[list["EvidenceAttachment"]] = relationship(back_populates="evidence_note")


class EvidenceAttachment(Base):
    """Metadata-only evidence attachment record."""

    __tablename__ = "evidence_attachments"

    attachment_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    evidence_id: Mapped[str] = mapped_column(
        ForeignKey("evidence_notes.evidence_id"),
        nullable=False,
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    storage_reference: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    evidence_note: Mapped[EvidenceNote] = relationship(back_populates="attachments")

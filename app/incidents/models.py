"""Incident ORM models."""

from sqlalchemy import JSON, Boolean, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import IncidentSeverity, IncidentStatus
from app.common.models import TimestampMixin
from app.common.types import enum_column, new_uuid, uuid_string
from app.database import Base


class Incident(TimestampMixin, Base):
    """Synthetic security incident record."""

    __tablename__ = "incidents"

    incident_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        enum_column(IncidentSeverity),
        nullable=False,
        default=IncidentSeverity.LOW,
    )
    status: Mapped[IncidentStatus] = mapped_column(
        enum_column(IncidentStatus),
        nullable=False,
        default=IncidentStatus.OPEN,
    )
    created_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    mitre_tactic: Mapped[str | None] = mapped_column(String(120), nullable=True)
    mitre_technique: Mapped[str | None] = mapped_column(String(120), nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # String annotations let SQLAlchemy resolve related models from its registry without imports.
    creator: Mapped["User"] = relationship(  # noqa: F821
        back_populates="created_incidents",
        foreign_keys=[created_by],
    )
    tickets: Mapped[list["Ticket"]] = relationship(back_populates="incident")  # noqa: F821
    evidence_notes: Mapped[list["EvidenceNote"]] = relationship(  # noqa: F821
        back_populates="incident"
    )
    remediation_tasks: Mapped[list["RemediationTask"]] = relationship(  # noqa: F821
        back_populates="incident"
    )

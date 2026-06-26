"""Remediation task ORM models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import RemediationStatus
from app.common.models import TimestampMixin
from app.common.types import enum_column, new_uuid, uuid_string
from app.database import Base

if TYPE_CHECKING:
    from app.incidents.models import Incident


class RemediationTask(TimestampMixin, Base):
    """Remediation task associated with an incident."""

    __tablename__ = "remediation_tasks"

    task_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    owner: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    status: Mapped[RemediationStatus] = mapped_column(
        enum_column(RemediationStatus),
        nullable=False,
        default=RemediationStatus.PENDING,
    )
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    incident: Mapped["Incident"] = relationship(back_populates="remediation_tasks")

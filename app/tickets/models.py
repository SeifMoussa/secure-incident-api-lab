"""Ticket ORM models."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import TicketPriority, TicketStatus
from app.common.models import TimestampMixin
from app.common.types import enum_column, new_uuid, uuid_string
from app.database import Base

if TYPE_CHECKING:
    from app.incidents.models import Incident


class Ticket(TimestampMixin, Base):
    """Ticket record within an incident."""

    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    incident_id: Mapped[str] = mapped_column(ForeignKey("incidents.incident_id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        enum_column(TicketStatus),
        nullable=False,
        default=TicketStatus.OPEN,
    )
    priority: Mapped[TicketPriority] = mapped_column(
        enum_column(TicketPriority),
        nullable=False,
        default=TicketPriority.P3,
    )
    assigned_to: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    incident: Mapped["Incident"] = relationship(back_populates="tickets")

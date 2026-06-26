"""Audit log ORM models."""

from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import AuditAction, AuditOutcome
from app.common.models import utc_now
from app.common.types import enum_column, new_uuid, uuid_string
from app.database import Base


class AuditLog(Base):
    """Append-only audit log model.

    Phase 2 defines the table only. Audit middleware and write services are later phases.
    """

    __tablename__ = "audit_log"

    audit_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.user_id"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(enum_column(AuditAction), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    changes: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    outcome: Mapped[AuditOutcome] = mapped_column(enum_column(AuditOutcome), nullable=False)

"""Authentication-related ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.common.enums import Role
from app.common.models import TimestampMixin, utc_now
from app.common.types import enum_column, new_uuid, uuid_string
from app.database import Base


class User(TimestampMixin, Base):
    """User account record.

    Endpoint behavior, password verification, and JWT handling are intentionally out of scope
    for Phase 2.
    """

    __tablename__ = "users"

    user_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(enum_column(Role), nullable=False, default=Role.VIEWER)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # String annotations let SQLAlchemy resolve related models from its registry without imports.
    created_incidents: Mapped[list["Incident"]] = relationship(  # noqa: F821
        back_populates="creator",
        foreign_keys="Incident.created_by",
    )


class TokenBlocklist(Base):
    """Blocked or expired token identifier record.

    Stores token identifiers only, not raw token values.
    """

    __tablename__ = "token_blocklist"
    __table_args__ = (Index("ix_token_blocklist_jti_unique", "jti", unique=True),)

    token_id: Mapped[str] = mapped_column(uuid_string(), primary_key=True, default=new_uuid)
    jti: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    token_type: Mapped[str] = mapped_column(String(32), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

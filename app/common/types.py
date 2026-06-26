"""Shared SQLAlchemy column types."""

from collections.abc import Sequence
from enum import StrEnum
from uuid import uuid4

from sqlalchemy import Enum, String


def new_uuid() -> str:
    """Return a string UUID suitable for SQLite and PostgreSQL-compatible schemas."""
    return str(uuid4())


def enum_column(enum_type: type[StrEnum]) -> Enum:
    """Create a non-native enum for portable SQLite/PostgreSQL-compatible migrations."""
    return Enum(
        enum_type,
        values_callable=_enum_values,
        native_enum=False,
        validate_strings=True,
        length=max(len(member.value) for member in enum_type),
    )


def uuid_string() -> String:
    """Return a portable UUID string column type."""
    return String(36)


def _enum_values(enum_type: type[StrEnum]) -> Sequence[str]:
    return [member.value for member in enum_type]

"""Per-request audit context."""

from contextvars import ContextVar
from dataclasses import dataclass, field

from app.common.enums import AuditAction


@dataclass
class AuditContext:
    """Safe route-provided audit metadata."""

    resource_type: str | None = None
    resource_id: str | None = None
    action: AuditAction | None = None
    changed_fields: list[str] = field(default_factory=list)


_audit_context: ContextVar[AuditContext | None] = ContextVar("audit_context", default=None)


def set_audit_context(
    *,
    resource_type: str | None = None,
    resource_id: str | None = None,
    action: AuditAction | None = None,
    changed_fields: list[str] | None = None,
) -> None:
    """Set safe audit metadata for the active request."""
    _audit_context.set(
        AuditContext(
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            changed_fields=changed_fields or [],
        )
    )


def get_audit_context() -> AuditContext | None:
    """Return route-provided audit metadata for the active request."""
    return _audit_context.get()


def clear_audit_context() -> None:
    """Clear route-provided audit metadata."""
    _audit_context.set(None)

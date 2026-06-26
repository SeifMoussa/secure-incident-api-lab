"""Audit service operations."""

from typing import Any

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.audit.models import AuditLog
from app.audit.sanitizer import sanitize_audit_value
from app.audit.schemas import (
    AuditEntryResponse,
    AuditFilterParams,
    AuditListResponse,
    IncidentTimelineResponse,
)
from app.common.enums import AuditAction, AuditOutcome
from app.common.models import utc_now
from app.common.pagination import PaginationParams


def create_audit_entry(
    db: Session,
    *,
    actor_id: str | None,
    action: AuditAction,
    resource_type: str,
    resource_id: str | None,
    ip_address: str | None,
    changes: dict[str, Any],
    outcome: AuditOutcome,
) -> None:
    """Persist one sanitized audit entry."""
    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        timestamp=utc_now(),
        ip_address=ip_address,
        changes=sanitize_audit_value(changes),
        outcome=outcome,
    )
    db.add(entry)
    db.commit()


def list_audit_entries(
    db: Session,
    *,
    filters: AuditFilterParams,
    pagination: PaginationParams,
) -> AuditListResponse:
    """List audit entries newest-first with safe filters."""
    query = _apply_filters(select(AuditLog), filters)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    entries = db.scalars(
        query.order_by(
            AuditLog.timestamp.desc(),
            _newest_first_action_order(),
            AuditLog.audit_id.desc(),
        )
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return AuditListResponse(
        items=[audit_entry_response(entry) for entry in entries],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def incident_timeline_entries(db: Session, *, incident_id: str) -> IncidentTimelineResponse:
    """Return incident audit entries oldest-first."""
    entries = db.scalars(
        select(AuditLog)
        .where(AuditLog.resource_type == "incident", AuditLog.resource_id == incident_id)
        .order_by(AuditLog.timestamp.asc(), _oldest_first_action_order(), AuditLog.audit_id.asc())
    ).all()
    return IncidentTimelineResponse(
        incident_id=incident_id,
        items=[audit_entry_response(entry) for entry in entries],
        total=len(entries),
    )


def audit_entry_response(entry: AuditLog) -> AuditEntryResponse:
    """Convert an audit model into a safe response schema."""
    return AuditEntryResponse(
        audit_id=entry.audit_id,
        actor_id=entry.actor_id,
        action=entry.action,
        resource_type=entry.resource_type,
        resource_id=entry.resource_id,
        timestamp=entry.timestamp,
        ip_address=entry.ip_address,
        changes=sanitize_audit_value(entry.changes),
        outcome=entry.outcome,
    )


def _apply_filters(query, filters: AuditFilterParams):
    if filters.resource_type is not None:
        query = query.where(AuditLog.resource_type == filters.resource_type)
    if filters.resource_id is not None:
        query = query.where(AuditLog.resource_id == filters.resource_id)
    if filters.actor is not None:
        query = query.where(AuditLog.actor_id == filters.actor)
    if filters.action is not None:
        query = query.where(AuditLog.action == filters.action)
    if filters.outcome is not None:
        query = query.where(AuditLog.outcome == filters.outcome)
    return query


def _oldest_first_action_order():
    return case(
        (AuditLog.action == AuditAction.CREATE, 0),
        (AuditLog.action == AuditAction.LOGIN, 0),
        (AuditLog.action == AuditAction.UPDATE, 1),
        (AuditLog.action == AuditAction.LOGOUT, 2),
        (AuditLog.action == AuditAction.DELETE, 3),
        else_=4,
    )


def _newest_first_action_order():
    return case(
        (AuditLog.action == AuditAction.DELETE, 0),
        (AuditLog.action == AuditAction.LOGOUT, 1),
        (AuditLog.action == AuditAction.UPDATE, 2),
        (AuditLog.action == AuditAction.CREATE, 3),
        (AuditLog.action == AuditAction.LOGIN, 3),
        else_=4,
    )

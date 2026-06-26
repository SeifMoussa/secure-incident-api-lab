"""Incident service-layer operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.models import utc_now
from app.common.pagination import PaginationParams
from app.incidents.models import Incident
from app.incidents.schemas import (
    IncidentCreateRequest,
    IncidentDeleteResponse,
    IncidentFilterParams,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdateRequest,
)


class IncidentServiceError(ValueError):
    """Raised for expected safe incident workflow failures."""


def create_incident(
    db: Session,
    *,
    actor: User,
    payload: IncidentCreateRequest,
) -> IncidentResponse:
    """Create a synthetic incident owned by the authenticated actor."""
    _validate_assignee(db, payload.assigned_to)
    incident = Incident(
        title=payload.title,
        description=payload.description,
        severity=payload.severity,
        status=payload.status,
        created_by=actor.user_id,
        assigned_to=payload.assigned_to,
        mitre_tactic=payload.mitre_tactic,
        mitre_technique=payload.mitre_technique,
        tags=payload.tags,
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident_response(incident)


def list_incidents(
    db: Session,
    *,
    filters: IncidentFilterParams,
    pagination: PaginationParams,
) -> IncidentListResponse:
    """List non-deleted incidents with safe filters and pagination."""
    filtered_query = _apply_filters(select(Incident).where(Incident.is_deleted.is_(False)), filters)
    total = db.scalar(select(func.count()).select_from(filtered_query.subquery())) or 0
    incidents = db.scalars(
        filtered_query.order_by(Incident.created_at.desc(), Incident.title.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return IncidentListResponse(
        items=[incident_response(incident) for incident in incidents],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def get_incident(db: Session, incident_id: str) -> IncidentResponse:
    """Return one non-deleted incident."""
    return incident_response(_get_active_incident_or_raise(db, incident_id))


def update_incident(
    db: Session,
    *,
    incident_id: str,
    payload: IncidentUpdateRequest,
) -> IncidentResponse:
    """Update allowed incident fields only."""
    incident = _get_active_incident_or_raise(db, incident_id)
    update_data = payload.model_dump(exclude_unset=True)
    if "assigned_to" in update_data:
        _validate_assignee(db, update_data["assigned_to"])
    for field_name, value in update_data.items():
        setattr(incident, field_name, value)
    incident.updated_at = utc_now()
    db.commit()
    db.refresh(incident)
    return incident_response(incident)


def soft_delete_incident(db: Session, incident_id: str) -> IncidentDeleteResponse:
    """Soft-delete an incident without removing the database record."""
    incident = _get_active_incident_or_raise(db, incident_id)
    incident.is_deleted = True
    incident.updated_at = utc_now()
    db.commit()
    db.refresh(incident)
    return IncidentDeleteResponse(message="Incident deleted.", incident=incident_response(incident))


def incident_response(incident: Incident) -> IncidentResponse:
    """Convert an incident model into a safe response schema."""
    return IncidentResponse(
        incident_id=incident.incident_id,
        title=incident.title,
        description=incident.description,
        severity=incident.severity,
        status=incident.status,
        created_by=incident.created_by,
        assigned_to=incident.assigned_to,
        mitre_tactic=incident.mitre_tactic,
        mitre_technique=incident.mitre_technique,
        tags=incident.tags,
        is_deleted=incident.is_deleted,
        created_at=incident.created_at.isoformat(),
        updated_at=incident.updated_at.isoformat(),
    )


def _apply_filters(query, filters: IncidentFilterParams):
    if filters.severity is not None:
        query = query.where(Incident.severity == filters.severity)
    if filters.status is not None:
        query = query.where(Incident.status == filters.status)
    if filters.assigned_to is not None:
        query = query.where(Incident.assigned_to == filters.assigned_to)
    if filters.created_after is not None:
        query = query.where(Incident.created_at >= filters.created_after)
    if filters.created_before is not None:
        query = query.where(Incident.created_at <= filters.created_before)
    if filters.tag is not None:
        normalized_tag = filters.tag.strip().lower()
        query = query.where(Incident.tags.contains([normalized_tag]))
    return query


def _get_active_incident_or_raise(db: Session, incident_id: str) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None or incident.is_deleted:
        msg = "Incident not found."
        raise IncidentServiceError(msg)
    return incident


def _validate_assignee(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        msg = "Assigned user not found."
        raise IncidentServiceError(msg)

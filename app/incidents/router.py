"""Incident API routes."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.audit.schemas import IncidentTimelineResponse
from app.audit.service import incident_timeline_entries
from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import IncidentSeverity, IncidentStatus, Role
from app.common.pagination import PaginationParams, get_pagination_params
from app.common.validation import UUID_PATTERN
from app.database import get_db
from app.incidents.schemas import (
    IncidentCreateRequest,
    IncidentDeleteResponse,
    IncidentFilterParams,
    IncidentListResponse,
    IncidentResponse,
    IncidentUpdateRequest,
)
from app.incidents.service import (
    IncidentServiceError,
    create_incident,
    get_incident,
    list_incidents,
    soft_delete_incident,
    update_incident,
)

router = APIRouter(prefix="/incidents", tags=["incidents"])

read_incidents = require_any_role(Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR)
write_incidents = require_any_role(Role.ADMIN, Role.ANALYST)
delete_incidents = require_any_role(Role.ADMIN)


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident_route(
    payload: IncidentCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_incidents)],
) -> IncidentResponse:
    try:
        return create_incident(db, actor=current_user, payload=payload)
    except IncidentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/", response_model=IncidentListResponse)
def list_incidents_route(
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_user: Annotated[User, Depends(read_incidents)],
    severity: IncidentSeverity | None = None,
    status_filter: Annotated[IncidentStatus | None, Query(alias="status")] = None,
    assigned_to: Annotated[str | None, Query(pattern=UUID_PATTERN)] = None,
    created_after: datetime | None = None,
    created_before: datetime | None = None,
    tag: str | None = None,
) -> IncidentListResponse:
    _ = current_user
    filters = IncidentFilterParams(
        severity=severity,
        status=status_filter,
        assigned_to=assigned_to,
        created_after=created_after,
        created_before=created_before,
        tag=tag,
    )
    return list_incidents(db, filters=filters, pagination=pagination)


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(read_incidents)],
) -> IncidentResponse:
    _ = current_user
    try:
        return get_incident(db, incident_id)
    except IncidentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{incident_id}/timeline", response_model=IncidentTimelineResponse)
def get_incident_timeline_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(read_incidents)],
) -> IncidentTimelineResponse:
    _ = current_user
    try:
        get_incident(db, incident_id)
    except IncidentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return incident_timeline_entries(db, incident_id=incident_id)


@router.patch("/{incident_id}", response_model=IncidentResponse)
def update_incident_route(
    incident_id: str,
    payload: IncidentUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_incidents)],
) -> IncidentResponse:
    _ = current_user
    try:
        return update_incident(db, incident_id=incident_id, payload=payload)
    except IncidentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.delete("/{incident_id}", response_model=IncidentDeleteResponse)
def delete_incident_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(delete_incidents)],
) -> IncidentDeleteResponse:
    _ = current_user
    try:
        return soft_delete_incident(db, incident_id)
    except IncidentServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

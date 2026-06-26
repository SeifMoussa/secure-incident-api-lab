"""Nested incident remediation task routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import Role
from app.common.pagination import PaginationParams, get_pagination_params
from app.database import get_db
from app.remediation.schemas import (
    RemediationCreateRequest,
    RemediationDeleteResponse,
    RemediationListResponse,
    RemediationResponse,
    RemediationUpdateRequest,
)
from app.remediation.service import (
    RemediationServiceError,
    create_remediation,
    list_remediation,
    soft_delete_remediation,
    update_remediation,
)

router = APIRouter(prefix="/incidents/{incident_id}/remediation", tags=["remediation"])

read_remediation = require_any_role(Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR)
write_remediation = require_any_role(Role.ADMIN, Role.ANALYST)


@router.post("/", response_model=RemediationResponse, status_code=status.HTTP_201_CREATED)
def create_remediation_route(
    incident_id: str,
    payload: RemediationCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_remediation)],
) -> RemediationResponse:
    _ = current_user
    try:
        return create_remediation(db, incident_id=incident_id, payload=payload)
    except RemediationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/", response_model=RemediationListResponse)
def list_remediation_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_user: Annotated[User, Depends(read_remediation)],
) -> RemediationListResponse:
    _ = current_user
    try:
        return list_remediation(db, incident_id=incident_id, pagination=pagination)
    except RemediationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{task_id}", response_model=RemediationResponse)
def update_remediation_route(
    incident_id: str,
    task_id: str,
    payload: RemediationUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_remediation)],
) -> RemediationResponse:
    _ = current_user
    try:
        return update_remediation(db, incident_id=incident_id, task_id=task_id, payload=payload)
    except RemediationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{task_id}", response_model=RemediationDeleteResponse)
def delete_remediation_route(
    incident_id: str,
    task_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_remediation)],
) -> RemediationDeleteResponse:
    _ = current_user
    try:
        return soft_delete_remediation(db, incident_id=incident_id, task_id=task_id)
    except RemediationServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

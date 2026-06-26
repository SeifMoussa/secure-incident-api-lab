"""Nested incident evidence note routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import Role
from app.common.pagination import PaginationParams, get_pagination_params
from app.database import get_db
from app.evidence.schemas import (
    EvidenceCreateRequest,
    EvidenceDeleteResponse,
    EvidenceListResponse,
    EvidenceResponse,
    EvidenceUpdateRequest,
)
from app.evidence.service import (
    EvidenceServiceError,
    create_evidence,
    get_evidence,
    list_evidence,
    soft_delete_evidence,
    update_evidence,
)

router = APIRouter(prefix="/incidents/{incident_id}/evidence", tags=["evidence"])

read_evidence = require_any_role(Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR)
write_evidence = require_any_role(Role.ADMIN, Role.ANALYST)
delete_evidence = require_any_role(Role.ADMIN)


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def create_evidence_route(
    incident_id: str,
    payload: EvidenceCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_evidence)],
) -> EvidenceResponse:
    try:
        return create_evidence(db, incident_id=incident_id, actor=current_user, payload=payload)
    except EvidenceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/", response_model=EvidenceListResponse)
def list_evidence_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_user: Annotated[User, Depends(read_evidence)],
) -> EvidenceListResponse:
    _ = current_user
    try:
        return list_evidence(db, incident_id=incident_id, pagination=pagination)
    except EvidenceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence_route(
    incident_id: str,
    evidence_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(read_evidence)],
) -> EvidenceResponse:
    _ = current_user
    try:
        return get_evidence(db, incident_id=incident_id, evidence_id=evidence_id)
    except EvidenceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{evidence_id}", response_model=EvidenceResponse)
def update_evidence_route(
    incident_id: str,
    evidence_id: str,
    payload: EvidenceUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_evidence)],
) -> EvidenceResponse:
    try:
        return update_evidence(
            db,
            incident_id=incident_id,
            evidence_id=evidence_id,
            actor=current_user,
            payload=payload,
        )
    except EvidenceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{evidence_id}", response_model=EvidenceDeleteResponse)
def delete_evidence_route(
    incident_id: str,
    evidence_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(delete_evidence)],
) -> EvidenceDeleteResponse:
    _ = current_user
    try:
        return soft_delete_evidence(db, incident_id=incident_id, evidence_id=evidence_id)
    except EvidenceServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

"""Nested incident ticket routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.dependencies import require_any_role
from app.common.enums import Role
from app.common.pagination import PaginationParams, get_pagination_params
from app.database import get_db
from app.tickets.schemas import (
    TicketCreateRequest,
    TicketDeleteResponse,
    TicketListResponse,
    TicketResponse,
    TicketUpdateRequest,
)
from app.tickets.service import (
    TicketServiceError,
    create_ticket,
    get_ticket,
    list_tickets,
    soft_delete_ticket,
    update_ticket,
)

router = APIRouter(prefix="/incidents/{incident_id}/tickets", tags=["tickets"])

read_tickets = require_any_role(Role.ADMIN, Role.ANALYST, Role.VIEWER, Role.AUDITOR)
write_tickets = require_any_role(Role.ADMIN, Role.ANALYST)


@router.post("/", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket_route(
    incident_id: str,
    payload: TicketCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_tickets)],
) -> TicketResponse:
    try:
        return create_ticket(db, incident_id=incident_id, actor=current_user, payload=payload)
    except TicketServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/", response_model=TicketListResponse)
def list_tickets_route(
    incident_id: str,
    db: Annotated[Session, Depends(get_db)],
    pagination: Annotated[PaginationParams, Depends(get_pagination_params)],
    current_user: Annotated[User, Depends(read_tickets)],
) -> TicketListResponse:
    _ = current_user
    try:
        return list_tickets(db, incident_id=incident_id, pagination=pagination)
    except TicketServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket_route(
    incident_id: str,
    ticket_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(read_tickets)],
) -> TicketResponse:
    _ = current_user
    try:
        return get_ticket(db, incident_id=incident_id, ticket_id=ticket_id)
    except TicketServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.patch("/{ticket_id}", response_model=TicketResponse)
def update_ticket_route(
    incident_id: str,
    ticket_id: str,
    payload: TicketUpdateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_tickets)],
) -> TicketResponse:
    _ = current_user
    try:
        return update_ticket(db, incident_id=incident_id, ticket_id=ticket_id, payload=payload)
    except TicketServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.delete("/{ticket_id}", response_model=TicketDeleteResponse)
def delete_ticket_route(
    incident_id: str,
    ticket_id: str,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(write_tickets)],
) -> TicketDeleteResponse:
    _ = current_user
    try:
        return soft_delete_ticket(db, incident_id=incident_id, ticket_id=ticket_id)
    except TicketServiceError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

"""Ticket service-layer operations."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.models import utc_now
from app.common.pagination import PaginationParams
from app.incidents.models import Incident
from app.tickets.models import Ticket
from app.tickets.schemas import (
    TicketCreateRequest,
    TicketDeleteResponse,
    TicketListResponse,
    TicketResponse,
    TicketUpdateRequest,
)


class TicketServiceError(ValueError):
    """Raised for expected safe ticket workflow failures."""


def create_ticket(
    db: Session, *, incident_id: str, actor: User, payload: TicketCreateRequest
) -> TicketResponse:
    _get_active_incident_or_raise(db, incident_id)
    _validate_active_user(db, payload.assigned_to)
    ticket = Ticket(
        incident_id=incident_id,
        title=payload.title,
        description=payload.description,
        status=payload.status,
        priority=payload.priority,
        assigned_to=payload.assigned_to,
        due_date=payload.due_date,
        created_by=actor.user_id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket_response(ticket)


def list_tickets(
    db: Session, *, incident_id: str, pagination: PaginationParams
) -> TicketListResponse:
    _get_active_incident_or_raise(db, incident_id)
    query = select(Ticket).where(Ticket.incident_id == incident_id, Ticket.is_deleted.is_(False))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    tickets = db.scalars(
        query.order_by(Ticket.created_at.desc(), Ticket.title.asc())
        .offset(pagination.offset)
        .limit(pagination.page_size)
    ).all()
    return TicketListResponse(
        items=[ticket_response(ticket) for ticket in tickets],
        page=pagination.page,
        page_size=pagination.page_size,
        total=total,
    )


def get_ticket(db: Session, *, incident_id: str, ticket_id: str) -> TicketResponse:
    return ticket_response(_get_active_ticket_or_raise(db, incident_id, ticket_id))


def update_ticket(
    db: Session,
    *,
    incident_id: str,
    ticket_id: str,
    payload: TicketUpdateRequest,
) -> TicketResponse:
    ticket = _get_active_ticket_or_raise(db, incident_id, ticket_id)
    data = payload.model_dump(exclude_unset=True)
    if "assigned_to" in data:
        _validate_active_user(db, data["assigned_to"])
    for field_name, value in data.items():
        setattr(ticket, field_name, value)
    ticket.updated_at = utc_now()
    db.commit()
    db.refresh(ticket)
    return ticket_response(ticket)


def soft_delete_ticket(db: Session, *, incident_id: str, ticket_id: str) -> TicketDeleteResponse:
    ticket = _get_active_ticket_or_raise(db, incident_id, ticket_id)
    ticket.is_deleted = True
    ticket.updated_at = utc_now()
    db.commit()
    db.refresh(ticket)
    return TicketDeleteResponse(message="Ticket deleted.", ticket=ticket_response(ticket))


def ticket_response(ticket: Ticket) -> TicketResponse:
    return TicketResponse(
        ticket_id=ticket.ticket_id,
        incident_id=ticket.incident_id,
        title=ticket.title,
        description=ticket.description,
        status=ticket.status,
        priority=ticket.priority,
        assigned_to=ticket.assigned_to,
        due_date=ticket.due_date.isoformat() if ticket.due_date else None,
        created_by=ticket.created_by,
        is_deleted=ticket.is_deleted,
        created_at=ticket.created_at.isoformat(),
        updated_at=ticket.updated_at.isoformat(),
    )


def _get_active_incident_or_raise(db: Session, incident_id: str) -> Incident:
    incident = db.get(Incident, incident_id)
    if incident is None or incident.is_deleted:
        msg = "Incident not found."
        raise TicketServiceError(msg)
    return incident


def _get_active_ticket_or_raise(db: Session, incident_id: str, ticket_id: str) -> Ticket:
    _get_active_incident_or_raise(db, incident_id)
    ticket = db.get(Ticket, ticket_id)
    if ticket is None or ticket.is_deleted or ticket.incident_id != incident_id:
        msg = "Ticket not found."
        raise TicketServiceError(msg)
    return ticket


def _validate_active_user(db: Session, user_id: str | None) -> None:
    if user_id is None:
        return
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        msg = "Assigned user not found."
        raise TicketServiceError(msg)

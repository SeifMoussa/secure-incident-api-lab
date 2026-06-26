from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import IncidentSeverity, IncidentStatus, TicketPriority, TicketStatus
from app.incidents.models import Incident
from app.tickets.models import Ticket


def test_ticket_enum_values_are_correct() -> None:
    assert [status.value for status in TicketStatus] == ["OPEN", "IN_PROGRESS", "DONE", "BLOCKED"]
    assert [priority.value for priority in TicketPriority] == ["P1", "P2", "P3", "P4"]


def test_ticket_model_fields_exist() -> None:
    columns = set(Ticket.__table__.columns.keys())

    assert {
        "ticket_id",
        "incident_id",
        "title",
        "description",
        "status",
        "priority",
        "assigned_to",
        "due_date",
        "created_by",
        "is_deleted",
        "created_at",
        "updated_at",
    } <= columns


def test_ticket_relationship_and_defaults(db_session: Session) -> None:
    user = User(
        email="ticket-user@example.com",
        display_name="Synthetic Ticket User",
        password_hash="synthetic-hash-only",
    )
    db_session.add(user)
    db_session.flush()
    incident = Incident(
        title="Synthetic incident",
        description="Synthetic defensive incident record.",
        severity=IncidentSeverity.MEDIUM,
        status=IncidentStatus.OPEN,
        created_by=user.user_id,
    )
    db_session.add(incident)
    db_session.flush()

    ticket = Ticket(
        incident_id=incident.incident_id,
        title="Synthetic ticket",
        description="Synthetic ticket description.",
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.P2,
        due_date=datetime.now(UTC) + timedelta(days=3),
        created_by=user.user_id,
    )
    db_session.add(ticket)
    db_session.commit()
    db_session.refresh(incident)

    assert len(incident.tickets) == 1
    assert incident.tickets[0].is_deleted is False
    assert incident.tickets[0].priority == TicketPriority.P2

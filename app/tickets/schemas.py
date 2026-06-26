"""Pydantic schemas for incident tickets."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import TicketPriority, TicketStatus
from app.common.validation import UUID_PATTERN


class TicketStrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class TicketCreateRequest(TicketStrictSchema):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    status: TicketStatus = TicketStatus.OPEN
    priority: TicketPriority = TicketPriority.P3
    assigned_to: str | None = Field(
        default=None, min_length=36, max_length=36, pattern=UUID_PATTERN
    )
    due_date: datetime | None = None


class TicketUpdateRequest(TicketStrictSchema):
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=2000)
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    assigned_to: str | None = Field(
        default=None, min_length=36, max_length=36, pattern=UUID_PATTERN
    )
    due_date: datetime | None = None


class TicketResponse(TicketStrictSchema):
    ticket_id: str
    incident_id: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    assigned_to: str | None
    due_date: str | None
    created_by: str
    is_deleted: bool
    created_at: str
    updated_at: str


class TicketListResponse(TicketStrictSchema):
    items: list[TicketResponse]
    page: int
    page_size: int
    total: int


class TicketDeleteResponse(TicketStrictSchema):
    message: str
    ticket: TicketResponse

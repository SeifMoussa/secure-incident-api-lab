"""Audit API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import AuditAction, AuditOutcome


class AuditStrictSchema(BaseModel):
    """Base schema that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class AuditEntryResponse(AuditStrictSchema):
    audit_id: str
    actor_id: str | None
    action: AuditAction
    resource_type: str
    resource_id: str | None
    timestamp: datetime
    ip_address: str | None
    changes: dict[str, Any] = Field(default_factory=dict)
    outcome: AuditOutcome


class AuditListResponse(AuditStrictSchema):
    items: list[AuditEntryResponse]
    page: int
    page_size: int
    total: int


class AuditFilterParams(AuditStrictSchema):
    resource_type: str | None = None
    resource_id: str | None = None
    actor: str | None = None
    action: AuditAction | None = None
    outcome: AuditOutcome | None = None


class IncidentTimelineResponse(AuditStrictSchema):
    incident_id: str
    items: list[AuditEntryResponse]
    total: int

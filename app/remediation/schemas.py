"""Pydantic schemas for remediation tasks."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.common.enums import RemediationStatus
from app.common.validation import UUID_PATTERN


class RemediationStrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RemediationCreateRequest(RemediationStrictSchema):
    action: str = Field(min_length=1, max_length=2000)
    owner: str | None = Field(default=None, min_length=36, max_length=36, pattern=UUID_PATTERN)
    status: RemediationStatus = RemediationStatus.PENDING
    deadline: datetime | None = None
    completion_notes: str | None = Field(default=None, max_length=2000)


class RemediationUpdateRequest(RemediationStrictSchema):
    action: str | None = Field(default=None, min_length=1, max_length=2000)
    owner: str | None = Field(default=None, min_length=36, max_length=36, pattern=UUID_PATTERN)
    status: RemediationStatus | None = None
    deadline: datetime | None = None
    completion_notes: str | None = Field(default=None, max_length=2000)


class RemediationResponse(RemediationStrictSchema):
    task_id: str
    incident_id: str
    action: str
    owner: str | None
    status: RemediationStatus
    deadline: str | None
    completion_notes: str | None
    completed_at: str | None
    is_deleted: bool
    created_at: str
    updated_at: str


class RemediationListResponse(RemediationStrictSchema):
    items: list[RemediationResponse]
    page: int
    page_size: int
    total: int


class RemediationDeleteResponse(RemediationStrictSchema):
    message: str
    task: RemediationResponse

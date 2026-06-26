"""Pydantic schemas for incident endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.common.enums import IncidentSeverity, IncidentStatus
from app.common.validation import UUID_PATTERN
from app.incidents.validators import normalize_tags, validate_mitre_tactic, validate_mitre_technique


class IncidentStrictSchema(BaseModel):
    """Base incident schema that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class IncidentCreateRequest(IncidentStrictSchema):
    title: str = Field(min_length=5, max_length=200)
    description: str = Field(min_length=1, max_length=5000)
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    assigned_to: str | None = Field(
        default=None, min_length=36, max_length=36, pattern=UUID_PATTERN
    )
    mitre_tactic: str | None = Field(default=None, max_length=120)
    mitre_technique: str | None = Field(default=None, max_length=120)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("mitre_tactic")
    @classmethod
    def validate_tactic(cls, value: str | None) -> str | None:
        return validate_mitre_tactic(value)

    @field_validator("mitre_technique")
    @classmethod
    def validate_technique(cls, value: str | None) -> str | None:
        return validate_mitre_technique(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        for tag in value:
            if len(tag.strip()) > 50:
                msg = "Tags must be 50 characters or fewer."
                raise ValueError(msg)
        return normalize_tags(value)


class IncidentUpdateRequest(IncidentStrictSchema):
    title: str | None = Field(default=None, min_length=5, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=5000)
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    assigned_to: str | None = Field(
        default=None, min_length=36, max_length=36, pattern=UUID_PATTERN
    )
    mitre_tactic: str | None = Field(default=None, max_length=120)
    mitre_technique: str | None = Field(default=None, max_length=120)
    tags: list[str] | None = Field(default=None, max_length=10)

    @field_validator("mitre_tactic")
    @classmethod
    def validate_tactic(cls, value: str | None) -> str | None:
        return validate_mitre_tactic(value)

    @field_validator("mitre_technique")
    @classmethod
    def validate_technique(cls, value: str | None) -> str | None:
        return validate_mitre_technique(value)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str] | None) -> list[str] | None:
        if value is None:
            return None
        for tag in value:
            if len(tag.strip()) > 50:
                msg = "Tags must be 50 characters or fewer."
                raise ValueError(msg)
        return normalize_tags(value)


class IncidentFilterParams(IncidentStrictSchema):
    severity: IncidentSeverity | None = None
    status: IncidentStatus | None = None
    assigned_to: str | None = Field(default=None, pattern=UUID_PATTERN)
    created_after: datetime | None = None
    created_before: datetime | None = None
    tag: str | None = None


class IncidentResponse(IncidentStrictSchema):
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    status: IncidentStatus
    created_by: str
    assigned_to: str | None
    mitre_tactic: str | None
    mitre_technique: str | None
    tags: list[str]
    is_deleted: bool
    created_at: str
    updated_at: str


class IncidentListResponse(IncidentStrictSchema):
    items: list[IncidentResponse]
    page: int
    page_size: int
    total: int


class IncidentDeleteResponse(IncidentStrictSchema):
    message: str
    incident: IncidentResponse

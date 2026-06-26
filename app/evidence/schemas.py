"""Pydantic schemas for evidence notes and metadata-only attachments."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.incidents.validators import normalize_tags


class EvidenceStrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class EvidenceAttachmentRequest(EvidenceStrictSchema):
    filename: str = Field(min_length=1, max_length=255, pattern=r"^[^\\/]+$")
    content_type: str = Field(
        min_length=1, max_length=120, pattern=r"^[A-Za-z0-9.+_-]+/[A-Za-z0-9.+_-]+$"
    )
    size_bytes: int = Field(ge=0)
    storage_reference: str = Field(min_length=1, max_length=255)


class EvidenceAttachmentResponse(EvidenceStrictSchema):
    attachment_id: str
    filename: str
    content_type: str
    size_bytes: int
    storage_reference: str
    created_at: str


class EvidenceCreateRequest(EvidenceStrictSchema):
    content: str = Field(min_length=1, max_length=10000)
    source: str = Field(min_length=1, max_length=200)
    collected_at: datetime
    tags: list[str] = Field(default_factory=list, max_length=10)
    attachments: list[EvidenceAttachmentRequest] = Field(default_factory=list, max_length=10)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, value: list[str]) -> list[str]:
        for tag in value:
            if len(tag.strip()) > 50:
                msg = "Tags must be 50 characters or fewer."
                raise ValueError(msg)
        return normalize_tags(value)


class EvidenceUpdateRequest(EvidenceStrictSchema):
    content: str | None = Field(default=None, min_length=1, max_length=10000)
    source: str | None = Field(default=None, min_length=1, max_length=200)
    collected_at: datetime | None = None
    tags: list[str] | None = Field(default=None, max_length=10)
    attachments: list[EvidenceAttachmentRequest] | None = Field(default=None, max_length=10)

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


class EvidenceResponse(EvidenceStrictSchema):
    evidence_id: str
    incident_id: str
    content: str
    source: str
    collected_at: str
    created_by: str
    tags: list[str]
    is_deleted: bool
    created_at: str
    updated_at: str
    attachments: list[EvidenceAttachmentResponse]


class EvidenceListResponse(EvidenceStrictSchema):
    items: list[EvidenceResponse]
    page: int
    page_size: int
    total: int


class EvidenceDeleteResponse(EvidenceStrictSchema):
    message: str
    evidence: EvidenceResponse

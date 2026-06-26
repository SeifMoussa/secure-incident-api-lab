"""Schemas for ADMIN-only user management."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.common.enums import Role


class AdminStrictSchema(BaseModel):
    """Base admin schema that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class AdminUserResponse(AdminStrictSchema):
    user_id: str
    email: EmailStr
    display_name: str
    role: Role
    is_active: bool
    created_at: str
    updated_at: str


class AdminUserListResponse(AdminStrictSchema):
    items: list[AdminUserResponse]
    page: int
    page_size: int
    total: int


class AdminRoleUpdateRequest(AdminStrictSchema):
    role: Role = Field(description="New role for the target user.")


class AdminDeactivateResponse(AdminStrictSchema):
    message: str
    user: AdminUserResponse

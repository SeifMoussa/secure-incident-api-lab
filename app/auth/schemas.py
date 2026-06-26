"""Pydantic schemas for authentication endpoints."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.common.enums import Role


class StrictSchema(BaseModel):
    """Base schema that rejects unexpected fields."""

    model_config = ConfigDict(extra="forbid")


class RegisterRequest(StrictSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)


class LoginRequest(StrictSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(StrictSchema):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(StrictSchema):
    refresh_token: str = Field(min_length=1)


class TokenResponse(StrictSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105


class AccessTokenResponse(StrictSchema):
    access_token: str
    token_type: str = "bearer"  # noqa: S105


class UserProfileResponse(StrictSchema):
    user_id: str
    email: EmailStr
    display_name: str
    role: Role
    is_active: bool


class AuthMessageResponse(StrictSchema):
    message: str

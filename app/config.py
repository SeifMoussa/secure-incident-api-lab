"""Application configuration for the Secure Incident Management API."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

EnvironmentName = Literal["development", "test", "production"]

LOCAL_SECRET_PLACEHOLDER = "CHANGE_ME_FOR_LOCAL_DEVELOPMENT"  # noqa: S105
LOCAL_CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]


class Settings(BaseSettings):
    """Environment-backed application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Secure Incident Management API"
    version: str = "0.1.0"
    environment: EnvironmentName = "development"
    debug: bool = False
    api_prefix: str = "/api"
    docs_enabled: bool = True
    database_url: str = "sqlite:///./dev-placeholder.sqlite3"
    jwt_secret_key: str | None = Field(default=None, repr=False)
    access_token_minutes: int = 15
    refresh_token_days: int = 7
    cors_allowed_origins: list[str] = Field(default_factory=list)
    rate_limit_enabled: bool = True
    rate_limit_login_per_minute: int = 10
    rate_limit_default_per_minute: int = 60
    rate_limit_window_seconds: int = 60
    https_redirect_enabled: bool = False
    hsts_max_age_seconds: int = 31_536_000

    @field_validator("api_prefix")
    @classmethod
    def api_prefix_must_start_with_slash(cls, value: str) -> str:
        if not value.startswith("/"):
            msg = "api_prefix must start with /"
            raise ValueError(msg)
        return value.rstrip("/") or "/"

    @field_validator("access_token_minutes", "refresh_token_days")
    @classmethod
    def token_durations_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            msg = "token duration values must be positive"
            raise ValueError(msg)
        return value

    @field_validator(
        "rate_limit_login_per_minute",
        "rate_limit_default_per_minute",
        "rate_limit_window_seconds",
        "hsts_max_age_seconds",
    )
    @classmethod
    def security_control_durations_must_be_positive(cls, value: int) -> int:
        if value <= 0:
            msg = "security control numeric values must be positive"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def production_requires_real_secret(self) -> "Settings":
        if self.environment == "production" and (
            not self.jwt_secret_key or self.jwt_secret_key == LOCAL_SECRET_PLACEHOLDER
        ):
            msg = "production requires JWT_SECRET_KEY from the environment"
            raise ValueError(msg)
        return self

    @property
    def docs_are_enabled(self) -> bool:
        """Disable interactive API docs whenever production settings are active."""
        return self.docs_enabled and self.environment != "production"

    @property
    def effective_cors_allowed_origins(self) -> list[str]:
        """Return the CORS allowlist for the active environment."""
        if self.cors_allowed_origins:
            return [origin for origin in self.cors_allowed_origins if origin != "*"]
        if self.environment == "production":
            return []
        return LOCAL_CORS_ORIGINS.copy()

    @property
    def https_redirect_is_enabled(self) -> bool:
        """Enable HTTPS redirects in production or when explicitly requested."""
        return self.environment == "production" or self.https_redirect_enabled

    @property
    def hsts_is_enabled(self) -> bool:
        """Enable HSTS only for production-like HTTPS behavior."""
        return self.environment == "production" or self.https_redirect_enabled


@lru_cache
def get_settings() -> Settings:
    """Return cached settings loaded from environment variables and optional .env."""
    try:
        return Settings()
    except ValidationError:
        raise

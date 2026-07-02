import pytest
from pydantic import ValidationError

from app.config import LOCAL_SECRET_PLACEHOLDER, Settings


def test_settings_load_with_safe_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in [
        "ENVIRONMENT",
        "JWT_SECRET_KEY",
        "RATE_LIMIT_ENABLED",
        "DATABASE_URL",
    ]:
        monkeypatch.delenv(key, raising=False)

    settings = Settings()

    assert settings.app_name == "Secure Incident Management API"
    assert settings.environment == "development"
    assert settings.api_prefix == "/api"
    assert settings.docs_are_enabled is True
    assert settings.jwt_secret_key is None
    assert settings.access_token_minutes == 15
    assert settings.refresh_token_days == 7
    assert settings.rate_limit_enabled is True


def test_api_prefix_is_normalized() -> None:
    settings = Settings(api_prefix="/api/")

    assert settings.api_prefix == "/api"


def test_api_prefix_must_start_with_slash() -> None:
    with pytest.raises(ValidationError, match="api_prefix"):
        Settings(api_prefix="api")


def test_token_durations_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="positive"):
        Settings(access_token_minutes=0)

    with pytest.raises(ValidationError, match="positive"):
        Settings(refresh_token_days=0)


def test_production_rejects_missing_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="production requires JWT_SECRET_KEY"):
        Settings(environment="production", jwt_secret_key=None)


def test_production_rejects_placeholder_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="production requires JWT_SECRET_KEY"):
        Settings(environment="production", jwt_secret_key=LOCAL_SECRET_PLACEHOLDER)


def test_production_accepts_environment_supplied_placeholder_for_future_secret() -> None:
    settings = Settings(
        environment="production",
        docs_enabled=True,
        jwt_secret_key="local-test-value-that-is-not-used-as-a-real-secret",  # noqa: S106
    )

    assert settings.docs_are_enabled is False
    assert settings.jwt_secret_key == "local-test-value-that-is-not-used-as-a-real-secret"  # noqa: S105

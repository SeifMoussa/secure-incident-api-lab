from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.common.enums import Role
from app.config import Settings, get_settings
from app.database import get_db
from app.main import create_app
from tests.auth_test_helpers import TEST_ONLY_PASSWORD, create_synthetic_user


@contextmanager
def client_with_settings(settings: Settings, db_session: Session) -> Iterator[TestClient]:
    app = create_app(settings)

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_settings] = lambda: settings
    with TestClient(app) as client:
        yield client


def test_login_rate_limit_can_trigger_429(db_session: Session) -> None:
    settings = Settings(
        environment="test",
        jwt_secret_key="synthetic-rate-limit-secret",
        rate_limit_enabled=True,
        rate_limit_login_per_minute=1,
        rate_limit_default_per_minute=100,
    )
    create_synthetic_user(db_session, email="rate-login@example.com", role=Role.ADMIN)

    with client_with_settings(settings, db_session) as client:
        first = client.post(
            "/auth/login",
            json={"email": "rate-login@example.com", "password": TEST_ONLY_PASSWORD},
        )
        second = client.post(
            "/auth/login",
            json={"email": "rate-login@example.com", "password": TEST_ONLY_PASSWORD},
        )

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.json() == {"detail": "Too many requests."}


def test_default_rate_limit_can_trigger_429(db_session: Session) -> None:
    settings = Settings(
        environment="test",
        jwt_secret_key="synthetic-rate-limit-secret",
        rate_limit_enabled=True,
        rate_limit_login_per_minute=100,
        rate_limit_default_per_minute=1,
    )

    with client_with_settings(settings, db_session) as client:
        first = client.get("/health")
        second = client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 429


def test_rate_limiting_disabled_setting_allows_repeated_requests(db_session: Session) -> None:
    settings = Settings(
        environment="test",
        jwt_secret_key="synthetic-rate-limit-secret",
        rate_limit_enabled=False,
        rate_limit_default_per_minute=1,
    )

    with client_with_settings(settings, db_session) as client:
        responses = [client.get("/health") for _ in range(3)]

    assert [response.status_code for response in responses] == [200, 200, 200]


def test_rate_limit_response_is_safe(db_session: Session) -> None:
    settings = Settings(
        environment="test",
        jwt_secret_key="synthetic-rate-limit-secret",
        rate_limit_enabled=True,
        rate_limit_default_per_minute=1,
    )

    with client_with_settings(settings, db_session) as client:
        client.get("/health")
        response = client.get("/health")

    forbidden = ["password", "token", "secret", "authorization", "api_key"]
    assert response.status_code == 429
    assert all(value not in response.text.lower() for value in forbidden)

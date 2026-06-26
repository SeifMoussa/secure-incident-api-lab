from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import TokenBlocklist
from app.auth.utils import REFRESH_TOKEN_TYPE, decode_token
from app.config import Settings

VALID_PASSWORD = "SyntheticRefresh!123"


def issue_tokens(client: TestClient, email: str = "refresh@example.com") -> dict[str, str]:
    register_response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": VALID_PASSWORD,
            "display_name": "Synthetic Refresh User",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": VALID_PASSWORD},
    )
    assert login_response.status_code == 200
    return login_response.json()


def test_refresh_success_returns_new_access_token(client: TestClient) -> None:
    tokens = issue_tokens(client)

    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert "refresh_token" not in body


def test_logout_blocklists_refresh_token_jti(
    client: TestClient,
    db_session: Session,
    test_settings: Settings,
) -> None:
    tokens = issue_tokens(client, "logout@example.com")
    payload = decode_token(test_settings, tokens["refresh_token"], expected_type=REFRESH_TOKEN_TYPE)

    response = client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out."}
    blocklisted = db_session.scalar(
        select(TokenBlocklist).where(TokenBlocklist.jti == payload["jti"])
    )
    assert blocklisted is not None
    assert blocklisted.token_type == REFRESH_TOKEN_TYPE


def test_refresh_after_logout_is_rejected(client: TestClient) -> None:
    tokens = issue_tokens(client, "refresh-after-logout@example.com")

    assert (
        client.post("/auth/logout", json={"refresh_token": tokens["refresh_token"]}).status_code
        == 200
    )
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid refresh token."


def test_logout_is_idempotent_for_invalid_token(client: TestClient) -> None:
    response = client.post("/auth/logout", json={"refresh_token": "invalid.synthetic.token"})

    assert response.status_code == 200
    assert response.json() == {"message": "Logged out."}

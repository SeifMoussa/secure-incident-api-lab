from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User

VALID_PASSWORD = "SyntheticLogin!123"


def register_user(client: TestClient, email: str = "login@example.com") -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": VALID_PASSWORD,
            "display_name": "Synthetic Login User",
        },
    )
    assert response.status_code == 201


def test_login_success_returns_tokens(client: TestClient) -> None:
    register_user(client)

    response = client.post(
        "/auth/login",
        json={"email": "login@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert "password_hash" not in response.text
    assert VALID_PASSWORD not in response.text


def test_login_wrong_password_is_generic(client: TestClient) -> None:
    register_user(client, "wrong-password@example.com")

    response = client.post(
        "/auth/login",
        json={"email": "wrong-password@example.com", "password": "WrongPassword!123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."


def test_inactive_user_cannot_login(client: TestClient, db_session: Session) -> None:
    register_user(client, "inactive@example.com")
    user = db_session.scalar(select(User).where(User.email == "inactive@example.com"))
    assert user is not None
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/auth/login",
        json={"email": "inactive@example.com", "password": VALID_PASSWORD},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password."

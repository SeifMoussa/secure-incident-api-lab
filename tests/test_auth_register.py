from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import User
from app.common.enums import Role

VALID_PASSWORD = "SyntheticRegister!123"


def test_register_success_returns_safe_profile(client: TestClient, db_session: Session) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "analyst@example.com",
            "password": VALID_PASSWORD,
            "display_name": "Synthetic Analyst",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "analyst@example.com"
    assert body["display_name"] == "Synthetic Analyst"
    assert body["role"] == Role.ANALYST
    assert body["is_active"] is True
    assert "password" not in body
    assert "password_hash" not in body

    user = db_session.scalar(select(User).where(User.email == "analyst@example.com"))
    assert user is not None
    assert user.password_hash != VALID_PASSWORD


def test_register_rejects_duplicate_email(client: TestClient) -> None:
    payload = {
        "email": "duplicate@example.com",
        "password": VALID_PASSWORD,
        "display_name": "Synthetic Analyst",
    }

    assert client.post("/auth/register", json=payload).status_code == 201
    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_rejects_invalid_email(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "not-an-email",
            "password": VALID_PASSWORD,
            "display_name": "Synthetic Analyst",
        },
    )

    assert response.status_code == 422


def test_register_rejects_common_password(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": "common-password@example.com",
            "password": "Password123!",
            "display_name": "Synthetic Analyst",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Password is too common."

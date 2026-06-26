from fastapi.testclient import TestClient

VALID_PASSWORD = "SyntheticMe!123"


def issue_tokens(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/auth/register",
        json={
            "email": "me@example.com",
            "password": VALID_PASSWORD,
            "display_name": "Synthetic Me User",
        },
    )
    assert response.status_code == 201
    login_response = client.post(
        "/auth/login",
        json={"email": "me@example.com", "password": VALID_PASSWORD},
    )
    assert login_response.status_code == 200
    return login_response.json()


def test_auth_me_returns_current_user_profile(client: TestClient) -> None:
    tokens = issue_tokens(client)

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {tokens['access_token']}"})

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "me@example.com"
    assert body["display_name"] == "Synthetic Me User"
    assert "password_hash" not in body


def test_auth_me_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Authentication credentials were not provided."


def test_auth_me_rejects_refresh_token(client: TestClient) -> None:
    tokens = issue_tokens(client)

    response = client.get(
        "/auth/me", headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials."

from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.auth.utils import (
    ACCESS_TOKEN_TYPE,
    JWT_ALGORITHM,
    REFRESH_TOKEN_TYPE,
    TokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
    extract_jti,
)
from app.config import Settings


def test_access_token_contains_expected_claims(test_settings: Settings) -> None:
    token = create_access_token(test_settings, user_id="synthetic-user-id", role="ANALYST")
    payload = decode_token(test_settings, token, expected_type=ACCESS_TOKEN_TYPE)

    assert payload["sub"] == "synthetic-user-id"
    assert payload["role"] == "ANALYST"
    assert payload["type"] == ACCESS_TOKEN_TYPE
    assert payload["jti"]


def test_refresh_token_contains_expected_type(test_settings: Settings) -> None:
    token = create_refresh_token(test_settings, user_id="synthetic-user-id", role="ANALYST")
    payload = decode_token(test_settings, token, expected_type=REFRESH_TOKEN_TYPE)

    assert payload["type"] == REFRESH_TOKEN_TYPE
    assert extract_jti(test_settings, token, expected_type=REFRESH_TOKEN_TYPE) == payload["jti"]


def test_decode_token_rejects_wrong_type(test_settings: Settings) -> None:
    token = create_refresh_token(test_settings, user_id="synthetic-user-id", role="ANALYST")

    with pytest.raises(TokenError, match="Invalid token type"):
        decode_token(test_settings, token, expected_type=ACCESS_TOKEN_TYPE)


def test_decode_token_rejects_expired_token(test_settings: Settings) -> None:
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "sub": "synthetic-user-id",
            "role": "ANALYST",
            "type": ACCESS_TOKEN_TYPE,
            "jti": "synthetic-jti",
            "iat": now - timedelta(minutes=30),
            "exp": now - timedelta(minutes=1),
        },
        test_settings.jwt_secret_key,
        algorithm=JWT_ALGORITHM,
    )

    with pytest.raises(TokenError, match="Invalid token"):
        decode_token(test_settings, token, expected_type=ACCESS_TOKEN_TYPE)


def test_token_creation_requires_secret() -> None:
    settings = Settings(environment="test", jwt_secret_key=None)

    with pytest.raises(TokenError, match="JWT secret is not configured"):
        create_access_token(settings, user_id="synthetic-user-id", role="ANALYST")

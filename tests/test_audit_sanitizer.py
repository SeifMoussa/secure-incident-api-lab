from app.audit.sanitizer import REDACTED, safe_field_summary, sanitize_audit_value


def test_sanitizer_redacts_sensitive_keys_recursively() -> None:
    value = {
        "email": "synthetic@example.com",
        "password": "SyntheticOnly!123",
        "nested": {
            "password_hash": "hash",
            "Authorization": "Bearer synthetic-token",
            "items": [{"api_key": "key"}, {"safe": "value"}],
        },
        "access_token": "header.payload.signature",
        "refresh_token": "header.payload.signature",
        "jwt_secret": "secret",
        "cookie": "session=value",
    }

    sanitized = sanitize_audit_value(value)

    assert sanitized["email"] == "synthetic@example.com"
    assert sanitized["password"] == REDACTED
    assert sanitized["nested"]["password_hash"] == REDACTED
    assert sanitized["nested"]["Authorization"] == REDACTED
    assert sanitized["nested"]["items"][0]["api_key"] == REDACTED
    assert sanitized["nested"]["items"][1]["safe"] == "value"
    assert sanitized["access_token"] == REDACTED
    assert sanitized["refresh_token"] == REDACTED
    assert sanitized["jwt_secret"] == REDACTED
    assert sanitized["cookie"] == REDACTED


def test_safe_field_summary_excludes_sensitive_field_names() -> None:
    summary = safe_field_summary(
        {
            "title": "Synthetic",
            "password": "SyntheticOnly!123",
            "refresh_token": "token",
        }
    )

    assert summary["fields_changed"] == ["title"]
    assert summary["redacted_sensitive_fields"] is True


def test_sanitizer_redacts_secret_like_strings_without_partial_exposure() -> None:
    token = "aaaaaaaa.bbbbbbbb.cccccccc"
    bearer = f"Bearer {token}"
    api_key = "sk-synthetic-not-real-key"

    sanitized = sanitize_audit_value(
        {
            "nested": [token, bearer, api_key, "Cookie: synthetic=value"],
            "safe": "Synthetic field summary",
        }
    )

    assert sanitized["nested"] == [REDACTED, REDACTED, REDACTED, REDACTED]
    assert sanitized["safe"] == "Synthetic field summary"
    combined = str(sanitized)
    assert token not in combined
    assert bearer not in combined
    assert api_key not in combined

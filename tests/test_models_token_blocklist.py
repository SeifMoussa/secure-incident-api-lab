from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.auth.models import TokenBlocklist


def test_token_blocklist_model_fields_exist() -> None:
    columns = set(TokenBlocklist.__table__.columns.keys())

    assert {"token_id", "jti", "token_type", "expires_at", "created_at"} <= columns


def test_token_blocklist_defaults(db_session: Session) -> None:
    blocked_token = TokenBlocklist(
        jti="synthetic-refresh-jti",
        token_type="refresh",
        expires_at=datetime.now(UTC) + timedelta(days=7),
    )

    db_session.add(blocked_token)
    db_session.commit()
    db_session.refresh(blocked_token)

    assert blocked_token.token_id
    assert blocked_token.created_at is not None

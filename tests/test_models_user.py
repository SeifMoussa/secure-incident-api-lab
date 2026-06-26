from datetime import UTC, datetime, timedelta

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.auth.models import TokenBlocklist, User
from app.common.enums import Role


def test_role_enum_values_are_correct() -> None:
    assert [role.value for role in Role] == ["ADMIN", "ANALYST", "VIEWER", "AUDITOR"]


def test_user_model_fields_exist() -> None:
    columns = set(User.__table__.columns.keys())

    assert {
        "user_id",
        "email",
        "display_name",
        "password_hash",
        "role",
        "is_active",
        "created_at",
        "updated_at",
    } <= columns


def test_user_email_uniqueness_metadata_exists() -> None:
    email_column = User.__table__.columns["email"]
    indexes = {index.name for index in User.__table__.indexes}

    assert email_column.unique is True
    assert "ix_users_email" in indexes


def test_user_defaults_and_timestamps(db_session: Session) -> None:
    user = User(
        email="analyst@example.com",
        display_name="Synthetic Analyst",
        password_hash="synthetic-hash-only",
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.user_id
    assert user.role == Role.VIEWER
    assert user.is_active is True
    assert user.created_at is not None
    assert user.updated_at is not None


def test_token_blocklist_has_unique_jti() -> None:
    jti_column = TokenBlocklist.__table__.columns["jti"]
    index_names = {index.name for index in TokenBlocklist.__table__.indexes}

    assert jti_column.unique is True
    assert "ix_token_blocklist_jti_unique" in index_names


def test_token_blocklist_persists_identifier_only(db_session: Session) -> None:
    token = TokenBlocklist(
        jti="synthetic-jti",
        token_type="refresh",
        expires_at=datetime.now(UTC) + timedelta(days=1),
    )

    db_session.add(token)
    db_session.commit()
    db_session.refresh(token)

    persisted_columns = set(inspect(TokenBlocklist).columns.keys())
    assert "token" not in persisted_columns
    assert "token_hash" not in persisted_columns
    assert token.jti == "synthetic-jti"

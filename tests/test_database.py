from contextlib import suppress

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from app.database import (
    Base,
    create_db_engine,
    create_session_factory,
    get_db,
    import_model_modules,
)

EXPECTED_TABLES = {
    "users",
    "incidents",
    "tickets",
    "evidence_notes",
    "evidence_attachments",
    "remediation_tasks",
    "audit_log",
    "token_blocklist",
}


def test_tables_can_be_created_in_sqlite(test_engine) -> None:
    table_names = set(inspect(test_engine).get_table_names())

    assert table_names >= EXPECTED_TABLES


def test_model_metadata_contains_expected_tables() -> None:
    import_model_modules()

    assert set(Base.metadata.tables) >= EXPECTED_TABLES


def test_create_db_engine_supports_sqlite_memory() -> None:
    engine = create_db_engine("sqlite+pysqlite:///:memory:")

    try:
        assert engine.url.database == ":memory:"
    finally:
        engine.dispose()


def test_create_session_factory_returns_session() -> None:
    engine = create_db_engine("sqlite+pysqlite:///:memory:")
    session_factory = create_session_factory(engine)

    try:
        session = session_factory()
        try:
            assert isinstance(session, Session)
        finally:
            session.close()
    finally:
        engine.dispose()


def test_get_db_yields_session() -> None:
    db_generator = get_db()
    session = next(db_generator)

    try:
        assert isinstance(session, Session)
    finally:
        with suppress(StopIteration):
            next(db_generator)

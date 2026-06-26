"""Database foundation for SQLAlchemy models and sessions."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def create_db_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the configured database URL."""
    resolved_url = database_url or get_settings().database_url
    connect_args = {"check_same_thread": False} if resolved_url.startswith("sqlite") else {}
    return create_engine(resolved_url, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Create a configured SQLAlchemy session factory."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


engine = create_db_engine()
SessionLocal = create_session_factory(engine)


def get_db() -> Generator[Session]:
    """Yield a database session for future FastAPI dependencies."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def import_model_modules() -> None:
    """Import ORM model modules so Alembic and tests can see full metadata."""
    import app.audit.models  # noqa: F401
    import app.auth.models  # noqa: F401
    import app.evidence.models  # noqa: F401
    import app.incidents.models  # noqa: F401
    import app.remediation.models  # noqa: F401
    import app.tickets.models  # noqa: F401

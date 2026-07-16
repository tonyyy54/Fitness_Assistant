from collections.abc import Generator

from sqlalchemy.orm import Session

from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Provide a database session for each API request."""

    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "sqlite:///./thinkspaces.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, future=True
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def create_db_and_tables() -> None:
    """Initialize database tables if they do not already exist."""
    from .models import Base

    Base.metadata.create_all(bind=engine)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session without auto-commit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""
app/db/session.py

SQLAlchemy async-compatible engine and session factory for Neon PostgreSQL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.core.config import settings


from sqlalchemy.pool import StaticPool

engine = None
SessionLocal = None

if settings.database_url:
    connect_args = {}
    if settings.database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        # For in-memory, we need StaticPool to keep the DB alive across connections
        if settings.database_url == "sqlite:///:memory:":
            engine = create_engine(
                settings.database_url,
                connect_args=connect_args,
                poolclass=StaticPool,
            )
        else:
            engine = create_engine(settings.database_url, connect_args=connect_args)
        
        # Create tables immediately for SQLite
        from app.db.base import Base
        Base.metadata.create_all(bind=engine)
    else:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it is closed after the request.
    """
    if SessionLocal is None:
        # If no DB configured, we skip yielding or handle accordingly
        return

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

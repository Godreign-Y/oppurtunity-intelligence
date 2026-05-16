"""
Database connection and session management.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings
from app.core.base import Base  # ✅ changed import

settings = get_settings()


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db():
    """
    Yield database session.

    Yields:
        AsyncSession
    """
    async with AsyncSessionLocal() as session:
        yield session
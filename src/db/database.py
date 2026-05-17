from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from src.config.settings import settings

# Create async engine for Neon PostgreSQL
engine = create_async_engine(settings.neon_database_url, echo=True)

# Create an async session maker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """
    Dependency function to get database session.
    """
    async with AsyncSessionLocal() as session:
        yield session

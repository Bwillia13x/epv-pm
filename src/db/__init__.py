from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
import os

# Reuse declarative base from auth module for single metadata
from src.auth.models import Base  # noqa: E402

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://epv:password@localhost:5432/epv"
)

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def init_db() -> None:
    """Create all tables asynchronously."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
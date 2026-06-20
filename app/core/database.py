from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# One engine per process. It owns the connection pool — connections are
# reused across requests instead of being opened/closed each time.
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    pool_pre_ping=True,  # check a pooled connection is alive before handing it out
)

# Factory that mints a fresh AsyncSession per request.
# expire_on_commit=False so ORM objects stay usable after commit (needed for
# async FastAPI, where we serialize the response after committing).
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields a request-scoped session, closed automatically."""
    async with AsyncSessionLocal() as session:
        yield session

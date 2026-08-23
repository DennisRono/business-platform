from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from business_platform.core.config import settings

engine: AsyncEngine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=1800,  # 30 minutes
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a request-scoped session; commit on success, rollback on error."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

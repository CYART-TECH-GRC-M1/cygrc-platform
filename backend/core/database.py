from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import settings

try:
    engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG, future=True)
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
except Exception:  # pragma: no cover - database backend may not be configured in local scaffolding
    engine = None
    AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database backend is not configured. Set DATABASE_URL to a valid async SQLAlchemy URL."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

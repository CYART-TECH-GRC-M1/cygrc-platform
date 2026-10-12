
import asyncio
import os
from pathlib import Path

import pytest

# Configure an isolated test database BEFORE importing application modules.
TEST_DB_PATH = Path(".pytest_cache") / "cygrc_test.db"
TEST_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
os.environ["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite+aiosqlite:///./.pytest_cache/cygrc_test.db"
)

from backend.core.database import Base, engine, AsyncSessionLocal, get_db
from backend.core.security import create_access_token
import backend.models  # Register all ORM models
from backend.main import app


@pytest.fixture(scope="session", autouse=True)
def test_database():
    """Initialize the isolated database used by the application's shared engine."""

    async def setup_database():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def teardown_database():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def override_get_db():
        async with AsyncSessionLocal() as session:
            yield session

    asyncio.run(setup_database())
    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.pop(get_db, None)
    asyncio.run(teardown_database())

    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.fixture
def make_token():
    """Factory fixture: generates a JWT for a given user_id/tenant_id/role."""

    def _make_token(
        user_id: str = "test-user-id",
        tenant_id: str = "test-tenant-id",
        role: str = "Employee",
    ):
        return create_access_token(
            subject=user_id,
            tenant_id=tenant_id,
            role=role,
        )

    return _make_token

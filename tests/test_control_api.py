import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.core.database import engine


@pytest.mark.anyio
async def test_list_frameworks():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/frameworks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    await engine.dispose()


@pytest.mark.anyio
async def test_list_controls():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/controls/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    await engine.dispose()

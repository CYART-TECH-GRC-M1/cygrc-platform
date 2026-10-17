import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.core.database import engine


def _unique_domain():
    return f"test-{uuid.uuid4().hex[:8]}.com"


@pytest.mark.anyio
async def test_create_tenant_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/tenants/",
            json={
                "name": "Test Corp",
                "domain": _unique_domain(),
                "subscription_plan": "FREE",
            },
        )
    assert response.status_code == 201
    body = response.json()
    assert "tenant_id" in body
    assert body["name"] == "Test Corp"
    await engine.dispose()


@pytest.mark.anyio
async def test_create_tenant_duplicate_domain_rejected():
    domain = _unique_domain()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        first = await ac.post(
            "/api/v1/tenants/",
            json={"name": "Dup Corp", "domain": domain, "subscription_plan": "FREE"},
        )
        assert first.status_code == 201

        second = await ac.post(
            "/api/v1/tenants/",
            json={"name": "Dup Corp 2", "domain": domain, "subscription_plan": "FREE"},
        )
    assert second.status_code == 400
    await engine.dispose()


@pytest.mark.anyio
async def test_get_current_tenant_me():
    domain = _unique_domain()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        created = await ac.post(
            "/api/v1/tenants/",
            json={"name": "Me Corp", "domain": domain, "subscription_plan": "FREE"},
        )
        tenant_id = created.json()["tenant_id"]

        me = await ac.get(
            "/api/v1/tenants/me",
            headers={"X-Tenant-ID": tenant_id},
        )
    assert me.status_code == 200
    assert me.json()["tenant_id"] == tenant_id
    assert me.json()["domain"] == domain
    await engine.dispose()


@pytest.mark.anyio
async def test_list_tenants_without_admin_role_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/tenants/")
    # No Authorization header at all -> require_role's own check should reject
    assert response.status_code == 401
    await engine.dispose()

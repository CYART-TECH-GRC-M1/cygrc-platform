import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.core.database import engine


def _unique_domain():
    return f"test-{uuid.uuid4().hex[:8]}.com"


def _unique_email():
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


async def _create_tenant(ac):
    resp = await ac.post(
        "/api/v1/tenants/",
        json={"name": "User Test Corp", "domain": _unique_domain(), "subscription_plan": "FREE"},
    )
    return resp.json()["tenant_id"]


@pytest.mark.anyio
async def test_create_user_success():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        tenant_id = await _create_tenant(ac)

        response = await ac.post(
            "/api/v1/users/",
            headers={"X-Tenant-ID": tenant_id},
            json={"first_name": "Jane", "last_name": "Doe", "email": _unique_email()},
        )
    assert response.status_code == 201
    body = response.json()
    assert body["tenant_id"] == tenant_id
    assert body["first_name"] == "Jane"
    await engine.dispose()


@pytest.mark.anyio
async def test_create_user_missing_tenant_context_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/",
            json={"first_name": "No", "last_name": "Context", "email": _unique_email()},
        )
    assert response.status_code == 401
    await engine.dispose()


@pytest.mark.anyio
async def test_create_user_invalid_tenant_id_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/users/",
            headers={"X-Tenant-ID": "not-a-real-uuid"},
            json={"first_name": "Bad", "last_name": "UUID", "email": _unique_email()},
        )
    assert response.status_code == 400
    await engine.dispose()


@pytest.mark.anyio
async def test_create_user_duplicate_email_rejected():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        tenant_id = await _create_tenant(ac)
        email = _unique_email()

        first = await ac.post(
            "/api/v1/users/",
            headers={"X-Tenant-ID": tenant_id},
            json={"first_name": "First", "last_name": "One", "email": email},
        )
        assert first.status_code == 201

        second = await ac.post(
            "/api/v1/users/",
            headers={"X-Tenant-ID": tenant_id},
            json={"first_name": "Second", "last_name": "One", "email": email},
        )
    assert second.status_code == 400
    await engine.dispose()


@pytest.mark.anyio
async def test_tenant_isolation_user_not_visible_to_other_tenant():
    """Core zero-trust check: a user created under tenant A must not be
    fetchable using tenant B's context, even with the correct user_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        tenant_a = await _create_tenant(ac)
        tenant_b = await _create_tenant(ac)

        created = await ac.post(
            "/api/v1/users/",
            headers={"X-Tenant-ID": tenant_a},
            json={"first_name": "Isolated", "last_name": "User", "email": _unique_email()},
        )
        user_id = created.json()["user_id"]

        # Same user_id, wrong tenant context -> must not be visible
        cross_tenant_fetch = await ac.get(
            f"/api/v1/users/{user_id}",
            headers={"X-Tenant-ID": tenant_b},
        )
        assert cross_tenant_fetch.status_code == 404

        # Correct tenant context -> must be visible
        same_tenant_fetch = await ac.get(
            f"/api/v1/users/{user_id}",
            headers={"X-Tenant-ID": tenant_a},
        )
        assert same_tenant_fetch.status_code == 200
    await engine.dispose()

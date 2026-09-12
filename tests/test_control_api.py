import uuid
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.core.security import create_access_token


def _get_admin_headers():
    token = create_access_token(
        subject="00000000-0000-0000-0000-000000000001",
        tenant_id="00000000-0000-0000-0000-00000000000a",
        role="Admin",
    )
    return {"Authorization": f"Bearer {token}"}


def _get_employee_headers():
    token = create_access_token(
        subject="00000000-0000-0000-0000-000000000002",
        tenant_id="00000000-0000-0000-0000-00000000000a",
        role="Employee",
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.anyio
async def test_list_frameworks():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/frameworks/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_get_framework_details():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        fw_res = await ac.get("/api/v1/frameworks/")
        assert fw_res.status_code == 200
        frameworks = fw_res.json()
        if frameworks:
            fw_id = frameworks[0]["framework_id"]
            res = await ac.get(f"/api/v1/frameworks/{fw_id}")
            assert res.status_code == 200
            assert res.json()["framework_id"] == fw_id


@pytest.mark.anyio
async def test_list_controls():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/controls/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.anyio
async def test_create_and_update_control_with_rbac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Fetch an existing framework ID
        fw_res = await ac.get("/api/v1/frameworks/")
        frameworks = fw_res.json()
        if not frameworks:
            pytest.skip("No frameworks seeded to test control creation.")
        
        framework_id = frameworks[0]["framework_id"]
        control_code = f"TST-{uuid.uuid4().hex[:6].upper()}"

        # 1. Non-admin attempt should be blocked with 403 Forbidden
        emp_headers = _get_employee_headers()
        forbidden_res = await ac.post(
            "/api/v1/controls/",
            json={
                "framework_id": framework_id,
                "control_code": control_code,
                "control_name": "Test RBAC Blocked Control",
                "description": "Should fail with 403",
                "status": "ACTIVE",
            },
            headers=emp_headers,
        )
        assert forbidden_res.status_code == 403

        # 2. Admin attempt should succeed with 201 Created
        admin_headers = _get_admin_headers()
        create_res = await ac.post(
            "/api/v1/controls/",
            json={
                "framework_id": framework_id,
                "control_code": control_code,
                "control_name": "Test Security Policy Control",
                "description": "Created via Step 4 test",
                "status": "ACTIVE",
            },
            headers=admin_headers,
        )
        assert create_res.status_code == 201
        created_control = create_res.json()
        control_id = created_control["control_id"]
        assert created_control["control_code"] == control_code

        # 3. Fetch control by ID
        get_res = await ac.get(f"/api/v1/controls/{control_id}")
        assert get_res.status_code == 200
        assert get_res.json()["control_id"] == control_id

        # 4. Update control status to INACTIVE with Admin role
        update_res = await ac.put(
            f"/api/v1/controls/{control_id}",
            json={
                "control_name": "Updated Test Security Policy Control",
                "status": "INACTIVE",
            },
            headers=admin_headers,
        )
        assert update_res.status_code == 200
        assert update_res.json()["status"] == "INACTIVE"

import uuid
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
async def test_create_and_get_framework():
    unique_name = f"NIST Test {uuid.uuid4().hex[:6]}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create framework
        create_resp = await ac.post(
            "/api/v1/frameworks/",
            json={
                "framework_name": unique_name,
                "version": "2024",
                "description": "NIST Cybersecurity Framework 2.0 Test",
            },
        )
        assert create_resp.status_code == 201
        fw_data = create_resp.json()
        fw_id = fw_data["framework_id"]

        # Get framework by ID
        get_resp = await ac.get(f"/api/v1/frameworks/{fw_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["framework_name"] == unique_name

        # List controls under this framework
        ctrls_resp = await ac.get(f"/api/v1/frameworks/{fw_id}/controls")
        assert ctrls_resp.status_code == 200
        assert isinstance(ctrls_resp.json(), list)

    await engine.dispose()


@pytest.mark.anyio
async def test_create_update_delete_control():
    unique_name = f"PCI DSS {uuid.uuid4().hex[:6]}"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First ensure a framework exists
        fw_resp = await ac.post(
            "/api/v1/frameworks/",
            json={
                "framework_name": unique_name,
                "version": "4.0",
                "description": "Payment Card Industry Data Security Standard Test",
            },
        )
        assert fw_resp.status_code == 201
        fw_id = fw_resp.json()["framework_id"]

        # Create control
        ctrl_resp = await ac.post(
            "/api/v1/controls/",
            json={
                "framework_id": fw_id,
                "control_code": "REQ-1.1",
                "control_name": "Network Security Controls",
                "description": "Install and maintain network security controls",
                "status": "ACTIVE",
            },
        )
        assert ctrl_resp.status_code == 201
        ctrl_id = ctrl_resp.json()["control_id"]

        # Get control
        get_resp = await ac.get(f"/api/v1/controls/{ctrl_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["control_code"] == "REQ-1.1"

        # Update control
        update_resp = await ac.put(
            f"/api/v1/controls/{ctrl_id}",
            json={"control_name": "Updated Network Security Controls"},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["control_name"] == "Updated Network Security Controls"

        # Delete control
        del_resp = await ac.delete(f"/api/v1/controls/{ctrl_id}")
        assert del_resp.status_code == 204

    await engine.dispose()

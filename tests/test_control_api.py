from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_frameworks_and_controls_are_tenant_isolated():
    tenant_a = {"X-Tenant-ID": "tenant-a"}
    tenant_b = {"X-Tenant-ID": "tenant-b"}

    framework_response = client.get("/api/v1/frameworks", headers=tenant_a)
    assert framework_response.status_code == 200
    assert isinstance(framework_response.json(), list)

    create_response = client.post(
        "/api/v1/controls",
        headers=tenant_a,
        json={
            "name": "Access Control",
            "description": "Restrict unauthorized access.",
            "framework_id": 1,
            "status": "active",
        },
    )
    assert create_response.status_code == 201

    controls_a = client.get("/api/v1/controls", headers=tenant_a)
    assert controls_a.status_code == 200
    assert len(controls_a.json()) >= 1

    controls_b = client.get("/api/v1/controls", headers=tenant_b)
    assert controls_b.status_code == 200
    assert controls_b.json() == []

    update_response = client.put(
        "/api/v1/controls/1",
        headers=tenant_a,
        json={"name": "Updated Access Control", "status": "inactive"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Access Control"

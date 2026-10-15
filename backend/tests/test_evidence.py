from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.evidence import router
from backend.core.dependencies import get_current_user

app = FastAPI()
app.include_router(router, prefix="/api/v1/evidence")
client = TestClient(app)

BASE = "/api/v1/evidence"
FAKE_ID = "11111111-1111-1111-1111-111111111111"


def teardown_function():
    app.dependency_overrides.clear()


def test_routes_registered():
    paths = {r.path for r in router.routes}
    assert "/{evidence_id}/files" in paths
    assert "/{evidence_id}/files/{file_id}/download" in paths
    assert "/{evidence_id}/reviews" in paths


def test_list_requires_auth():
    assert client.get(f"{BASE}/").status_code == 401


def test_create_requires_auth():
    r = client.post(f"{BASE}/", json={"control_id": FAKE_ID, "title": "x"})
    assert r.status_code == 401


def test_upload_requires_auth():
    r = client.post(f"{BASE}/{FAKE_ID}/files", files={"file": ("a.txt", b"hi")})
    assert r.status_code == 401


def test_x_tenant_header_alone_is_rejected():
    r = client.get(f"{BASE}/", headers={"X-Tenant-ID": FAKE_ID})
    assert r.status_code == 401


def test_invalid_tenant_claim_rejected():
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": FAKE_ID,
        "tenant_id": "not-a-uuid",
    }
    assert client.get(f"{BASE}/").status_code == 401


def test_create_validates_body():
    app.dependency_overrides[get_current_user] = lambda: {
        "user_id": FAKE_ID,
        "tenant_id": FAKE_ID,
    }
    r = client.post(f"{BASE}/", json={"control_id": "bad", "title": ""})
    assert r.status_code == 422

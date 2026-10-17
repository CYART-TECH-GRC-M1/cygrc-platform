from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.evidence import router
from backend.core.dependencies import get_current_user

app = FastAPI()
app.include_router(router, prefix="/api/v1/evidence")
client = TestClient(app)

BASE = "/api/v1/evidence"
FAKE_ID = "11111111-1111-1111-1111-111111111111"
FORM = {"control_id": FAKE_ID, "title": "x"}
FILE = {"file": ("a.txt", b"hello")}


def teardown_function():
    app.dependency_overrides.clear()


def test_routes_registered():
    paths = {r.path for r in router.routes}
    assert {"/", "/{evidence_id}", "/{evidence_id}/verify"} <= paths


def test_upload_requires_auth():
    assert client.post(f"{BASE}/", data=FORM, files=FILE).status_code == 401


def test_list_requires_auth():
    assert client.get(f"{BASE}/").status_code == 401


def test_get_requires_auth():
    assert client.get(f"{BASE}/{FAKE_ID}").status_code == 401


def test_x_tenant_header_alone_is_rejected():
    assert client.get(f"{BASE}/", headers={"X-Tenant-ID": FAKE_ID}).status_code == 401


def test_invalid_tenant_claim_rejected():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": FAKE_ID, "tenant_id": "not-a-uuid"}
    assert client.get(f"{BASE}/").status_code == 401


def test_upload_rejects_bad_form():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": FAKE_ID, "tenant_id": FAKE_ID}
    r = client.post(f"{BASE}/", data={"control_id": "bad", "title": ""}, files=FILE)
    assert r.status_code == 422


def test_upload_rejects_disallowed_extension():
    app.dependency_overrides[get_current_user] = lambda: {"user_id": FAKE_ID, "tenant_id": FAKE_ID}
    r = client.post(f"{BASE}/", data=FORM, files={"file": ("evil.exe", b"MZ")})
    assert r.status_code == 400

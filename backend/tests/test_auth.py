"""
tests/test_auth.py

Runs completely standalone — no Docker, no Keycloak, no Postgres needed.
That's the actual advantage of this local-auth placeholder: everything
here is testable with nothing but `pytest`.
"""
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


# ---- Ask #1: login endpoint issues real signed JWTs -------------------

def test_login_with_correct_credentials_returns_token():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body and len(body["access_token"]) > 20
    assert body["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401():
    resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    assert resp.status_code == 401


def test_login_with_unknown_email_returns_401():
    resp = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "whatever"})
    assert resp.status_code == 401


def test_login_error_does_not_reveal_whether_user_exists():
    """Wrong password and unknown user should return the identical
    response — revealing which one it was makes it easier for an
    attacker to enumerate valid emails."""
    r1 = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
    r2 = client.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
    assert r1.status_code == r2.status_code == 401
    assert r1.json() == r2.json()


# ---- Ask #2: Bearer header interception/validation ---------------------

def test_protected_route_without_token_returns_401():
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401


def test_protected_route_with_garbage_token_returns_401():
    resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
    assert resp.status_code == 401


def test_protected_route_with_valid_token_returns_user_info():
    token = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass123"}).json()["access_token"]
    resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["role"] == "Admin"
    assert body["tenant_id"] == "00000000-0000-0000-0000-00000000000a"


# ---- Ask #3 + #4: require_role, 401/403 enforcement --------------------

def test_require_role_allows_matching_role():
    token = client.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass123"}).json()["access_token"]
    resp = client.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_require_role_blocks_wrong_role_with_403():
    token = client.post("/api/v1/auth/login", json={"email": "employee@test.com", "password": "employeepass123"}).json()["access_token"]
    resp = client.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_require_role_blocks_missing_token_with_401():
    resp = client.delete("/api/v1/auth/admin-only-test")
    assert resp.status_code == 401


# ---- Regression test: the cross-tenant spoofing bug, fixed -------------

def test_invalid_token_does_not_fall_back_to_client_supplied_tenant_header():
    """
    This is a regression test for a real bug found in the original
    dependencies.py: an invalid/expired Authorization header combined
    with a forged X-Tenant-ID header used to silently succeed and return
    the attacker's chosen tenant_id instead of rejecting the request.
    See README.md for the full writeup and the before/after proof.
    """
    from fastapi import Depends, FastAPI
    from backend.core.dependencies import get_current_tenant_id

    probe_app = FastAPI()

    @probe_app.get("/whoami-tenant")
    async def whoami_tenant(tenant_id: str = Depends(get_current_tenant_id)):
        return {"tenant_id": tenant_id}

    probe_client = TestClient(probe_app)

    resp = probe_client.get(
        "/whoami-tenant",
        headers={
            "Authorization": "Bearer this.is.garbage",
            "X-Tenant-ID": "ffffffff-ffff-ffff-ffff-ffffffffffff",
        },
    )
    assert resp.status_code == 401, (
        "An invalid Bearer token must NOT silently fall back to a "
        "client-supplied X-Tenant-ID header — that's a cross-tenant bug."
    )


def test_x_tenant_id_still_works_when_no_authorization_header_sent():
    """The legitimate dev/testing fallback path must still work."""
    from fastapi import Depends, FastAPI
    from backend.core.dependencies import get_current_tenant_id

    probe_app = FastAPI()

    @probe_app.get("/whoami-tenant")
    async def whoami_tenant(tenant_id: str = Depends(get_current_tenant_id)):
        return {"tenant_id": tenant_id}

    probe_client = TestClient(probe_app)

    resp = probe_client.get(
        "/whoami-tenant",
        headers={"X-Tenant-ID": "00000000-0000-0000-0000-00000000000a"},
    )
    assert resp.status_code == 200
    assert resp.json()["tenant_id"] == "00000000-0000-0000-0000-00000000000a"

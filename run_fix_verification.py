import sys
sys.path.insert(0, '.')

passed = 0
failed = 0

def check(name, cond, detail=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        print(f"  FAIL: {name} {detail}")

# ======== TEST: manual direct invocation pattern (root tests/test_auth.py style) ========
print("--- Direct invocation pattern (tests/test_auth.py style) ---")

import asyncio
from fastapi import HTTPException
from backend.core.dependencies import require_role
from backend.core.security import create_access_token

def make_token(user_id="tid", tenant_id="test-tenant-id", role="Employee"):
    return create_access_token(subject=user_id, tenant_id=tenant_id, role=role)

# Test: no parameter named 'authorization' error was the bug. This is the fix verification.
checker = require_role(["Admin", "Tenant Admin"])

# 1. valid admin token -> returns "Admin" string (not dict)
try:
    result = asyncio.run(checker(authorization=f"Bearer {make_token(role='Admin')}"))
    check("direct call: admin token -> returns 'Admin' string",
          result == "Admin",
          f"result={result!r} type={type(result).__name__}")
except TypeError as e:
    check("direct call: admin token -> returns 'Admin' string", False, f"TypeError: {e}")
except HTTPException as e:
    check("direct call: admin token -> returns 'Admin' string", False, f"HTTP {e.status_code}: {e.detail}")
except Exception as e:
    check("direct call: admin token -> returns 'Admin' string", False, f"{type(e).__name__}: {e}")

# 2. wrong role -> 403
try:
    asyncio.run(checker(authorization=f"Bearer {make_token(role='Employee')}"))
    check("direct call: employee blocked from Admin-only -> 403", False)
except HTTPException as e:
    check("direct call: employee blocked from Admin-only -> 403", e.status_code == 403, f"status={e.status_code}")
except Exception as e:
    check("direct call: employee blocked from Admin-only -> 403", False, f"{type(e).__name__}: {e}")

# 3. missing header -> 401
try:
    asyncio.run(checker(authorization=None))
    check("direct call: missing authorization -> 401", False)
except HTTPException as e:
    check("direct call: missing authorization -> 401", e.status_code == 401, f"status={e.status_code}")
except Exception as e:
    check("direct call: missing authorization -> 401", False, f"{type(e).__name__}: {e}")

# 4. malformed header -> 401
try:
    asyncio.run(checker(authorization="NotBearer sometoken"))
    check("direct call: malformed auth header -> 401", False)
except HTTPException as e:
    check("direct call: malformed auth header -> 401", e.status_code == 401, f"status={e.status_code}")
except Exception as e:
    check("direct call: malformed auth header -> 401", False, f"{type(e).__name__}: {e}")

# 5. garbage token -> 401
try:
    asyncio.run(checker(authorization="Bearer this.is.not.valid"))
    check("direct call: garbage token -> 401", False)
except HTTPException as e:
    check("direct call: garbage token -> 401", e.status_code == 401, f"status={e.status_code}")
except Exception as e:
    check("direct call: garbage token -> 401", False, f"{type(e).__name__}: {e}")

# 6. tenant_admin role passes via Admin-only allow list
try:
    result = asyncio.run(checker(authorization=f"Bearer {make_token(role='Tenant Admin')}"))
    check("direct call: Tenant Admin passes ['Admin', 'Tenant Admin']",
          result == "Tenant Admin",
          f"result={result!r}")
except Exception as e:
    check("direct call: Tenant Admin passes ['Admin', 'Tenant Admin']",
          False, f"{type(e).__name__}: {e}")

# ======== TEST: FastAPI endpoint invocation pattern (backend/tests style) ========
print()
print("--- FastAPI endpoint invocation pattern (backend/tests style) ---")

from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.api.v1.auth import router as auth_router

test_app = FastAPI()
test_app.include_router(auth_router, prefix="/api/v1")
tc = TestClient(test_app)

# Login to get token
r = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass123"})
assert r.status_code == 200, f"login failed: {r.status_code} {r.text}"
admin_tok = r.json()["access_token"]

# 7. Admin accesses admin-only route -> 200
r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {admin_tok}"})
check("endpoint: Admin admin-only-test -> 200", r.status_code == 200, f"status={r.status_code} body={r.text}")
if r.status_code == 200:
    body = r.json()
    check("endpoint: admin-only-test returns role in message",
          "Admin" in body.get("message", ""),
          f"message={body.get('message')}")

# 8. Employee blocked -> 403
emp_tok = tc.post("/api/v1/auth/login", json={"email": "employee@test.com", "password": "employeepass123"}).json()["access_token"]
r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {emp_tok}"})
check("endpoint: Employee admin-only-test -> 403", r.status_code == 403, f"status={r.status_code}")

# 9. No token -> 401
r = tc.delete("/api/v1/auth/admin-only-test")
check("endpoint: no token admin-only-test -> 401", r.status_code == 401, f"status={r.status_code}")

# 10. Tenant Admin passes admin-only route
ta_resp = tc.post("/api/v1/auth/login", json={"email": "tenant_admin@test.com", "password": "tenantadminpass123"})
check("endpoint: Tenant Admin login -> 200", ta_resp.status_code == 200, f"status={ta_resp.status_code}")
ta_tok = ta_resp.json()["access_token"]
r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {ta_tok}"})
check("endpoint: Tenant Admin admin-only-test -> 200", r.status_code == 200, f"status={r.status_code} body={r.text}")

# ======== /me endpoint (get_current_user) tests ========
print()
print("--- /me endpoint & get_current_user tests ---")

r = tc.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_tok}"})
check("/me: Admin valid token -> 200", r.status_code == 200, f"status={r.status_code} body={r.text}")
if r.status_code == 200:
    me = r.json()
    check("/me: role == Admin", me.get("role") == "Admin", f"role={me.get('role')!r}")
    check("/me: tenant_id present", me.get("tenant_id") is not None and me.get("tenant_id") != "")
    check("/me: has keycloak_id key", "keycloak_id" in me)
    check("/me: has roles key", "roles" in me)
    check("/me: has email key", "email" in me)

r = tc.get("/api/v1/auth/me")
check("/me: no token -> 401", r.status_code == 401, f"status={r.status_code}")

r = tc.get("/api/v1/auth/me", headers={"Authorization": "Bearer not.a.real.token"})
check("/me: garbage token -> 401", r.status_code == 401, f"status={r.status_code}")

# ======== Login endpoint tests ========
print()
print("--- Login endpoint tests ---")

r = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
check("login: wrong password -> 401", r.status_code == 401)
r1 = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
r2 = tc.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
check("login: wrong/unknown identical error (no enumeration)",
      r1.status_code == 401 and r2.status_code == 401 and r1.json() == r2.json(),
      f"r1={r1.json()} r2={r2.json()}")

# ======== Cross-tenant regression bug test ========
print()
print("--- Cross-tenant regression test ---")
from backend.core.dependencies import get_current_tenant_id
probe = FastAPI()
@probe.get("/t")
async def who(tid: str = Depends(get_current_tenant_id)):
    return {"tenant_id": tid}
pc = TestClient(probe)

ok, st = False, None
try:
    asyncio.run(get_current_tenant_id(authorization="Bearer garbage", x_tenant_id="evil-tenant"))
except HTTPException as e:
    ok = e.status_code == 401
    st = e.status_code
check("SEC FIX: invalid token + X-Tenant-ID -> 401 (no fallback)",
      ok, f"status={st}")

r = pc.get("/t", headers={"X-Tenant-ID": "dev-tid-only"})
check("SEC FIX: no token + X-Tenant-ID -> 200 (dev fallback)",
      r.status_code == 200 and r.json()["tenant_id"] == "dev-tid-only",
      f"status={r.status_code} body={r.text if r.status_code != 200 else r.json()}")

# ======== validate_token: Keycloak claim normalization via local path ========
print()
print("--- validate_token roundtrip / claim normalization ---")

from backend.core.security import validate_token, _normalize_claims, _extract_keycloak_roles

tok = create_access_token(subject="u-999", tenant_id="t-xyz", role="Auditor")
payload = validate_token(tok)
check("validate_token: sub claim", payload is not None and payload.get("sub") == "u-999",
      f"payload={payload!r}")
check("validate_token: tenant_id claim", payload is not None and payload.get("tenant_id") == "t-xyz")
check("validate_token: role claim", payload is not None and payload.get("role") == "Auditor")
check("validate_token: has roles list key", payload is not None and "roles" in payload)
check("validate_token: has keycloak_id key", payload is not None and "keycloak_id" in payload)
check("validate_token: has email key", payload is not None and "email" in payload)

# Keycloak-style payload with realm_access + resource_access
kc_claims = {
    "sub": "kc-abc-123",
    "tenant_id": "kc-tenant-42",
    "email": "bob@example.com",
    "given_name": "Bob",
    "family_name": "Jones",
    "realm_access": {"roles": ["default-roles", "Employee"]},
    "resource_access": {"cygrc-backend": {"roles": ["Tenant Admin"]}},
}
norm = _normalize_claims(kc_claims)
check("normalize: primary role picks Tenant Admin over Employee",
      norm["role"] == "Tenant Admin", f"got role={norm['role']!r}")
check("normalize: roles list contains both realm and client roles",
      "Employee" in norm["roles"] and "Tenant Admin" in norm["roles"],
      f"roles={norm['roles']}")
check("normalize: keycloak_id == sub", norm["keycloak_id"] == "kc-abc-123")
check("normalize: email populated", norm["email"] == "bob@example.com")
check("normalize: first/last name", norm["first_name"] == "Bob" and norm["last_name"] == "Jones")

print()
print(f"=== TOTAL: {passed} passed, {failed} failed ===")
sys.exit(0 if failed == 0 else 1)

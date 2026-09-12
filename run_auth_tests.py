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

print("--- security.py ---")

from backend.core.security import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
    validate_token,
    _normalize_claims,
    _extract_keycloak_roles,
)

h = get_password_hash("hello123")
check("hash+verify success", verify_password("hello123", h))
check("hash+verify wrong fails", not verify_password("wrong", h))

token = create_access_token(subject="u1", tenant_id="t1", role="Admin")
payload_raw = decode_token(token)
check("decode_token local JWT", payload_raw is not None and payload_raw["sub"] == "u1")

payload = validate_token(token)
check("validate_token local JWT role=Admin", payload is not None and payload["role"] == "Admin" and payload["sub"] == "u1")
check("validate_token local tenant_id", payload is not None and payload["tenant_id"] == "t1")

check("validate_token rejects garbage", validate_token("abc.def.ghi") is None)

from datetime import timedelta
expired = create_access_token("u", "t", "X", expires_delta=timedelta(seconds=-1))
check("validate_token rejects expired", validate_token(expired) is None)

kc_payload = {
    "sub": "kc-user-123",
    "email": "alice@example.com",
    "given_name": "Alice",
    "family_name": "Smith",
    "tenant_id": "t-abc",
    "realm_access": {"roles": ["default-roles", "Employee", "offline_access"]},
    "resource_access": {"cygrc-backend": {"roles": ["Tenant Admin"]}},
}
norm = _normalize_claims(kc_payload)
check("normalize email", norm["email"] == "alice@example.com")
check("normalize first_name", norm["first_name"] == "Alice")
check("normalize last_name", norm["last_name"] == "Smith")
check("normalize keycloak_id=sub", norm["keycloak_id"] == "kc-user-123")
check("normalize primary role picks higher priority", norm["role"] == "Tenant Admin")
roles_list = norm["roles"]
check("normalize roles list has 5 entries", len(roles_list) == 5, f"got {len(roles_list)}: {roles_list}")
check("normalize roles list contains Employee", "Employee" in roles_list)
check("normalize roles list contains Tenant Admin", "Tenant Admin" in roles_list)

kc_roles = _extract_keycloak_roles(kc_payload)
check("extract_keycloak_roles count", len(kc_roles) == 5, f"got {kc_roles}")

print()
print("--- dependencies.py ---")

from backend.core.dependencies import (
    _extract_bearer_token,
    get_current_user,
    get_current_tenant_id,
    require_role,
)
from fastapi import HTTPException
import asyncio

check("extract_bearer ok", _extract_bearer_token("Bearer abcdef") == "abcdef")

def raises(fn, expected_status):
    try:
        fn()
        return False, None
    except HTTPException as e:
        return e.status_code == expected_status, e.status_code

ok, st = raises(lambda: _extract_bearer_token(None), 401)
check("extract_bearer None -> 401", ok, f"got status {st}")
ok, st = raises(lambda: _extract_bearer_token("Basic xxx"), 401)
check("extract_bearer Basic -> 401", ok)

auth_header = f"Bearer {token}"
user = asyncio.run(get_current_user(authorization=auth_header))
check("get_current_user valid -> user_id=u1", user["user_id"] == "u1")
check("get_current_user valid -> role=Admin", user["role"] == "Admin")
check("get_current_user valid -> tenant_id=t1", user["tenant_id"] == "t1")
check("get_current_user valid -> roles list present", isinstance(user.get("roles"), list))

ok, st = raises(lambda: asyncio.run(get_current_user(authorization="Bearer not.valid.token")), 401)
check("get_current_user invalid -> 401", ok, f"got status {st}")
ok, st = raises(lambda: asyncio.run(get_current_user(authorization=None)), 401)
check("get_current_user missing -> 401", ok)

rc = require_role(["Admin", "Tenant Admin"])
u = asyncio.run(rc(authorization=auth_header))
check("require_role Admin passes Admin allow", isinstance(u, dict) and u["role"] == "Admin")

rc2 = require_role(["SuperAdmin"])
ok, st = raises(lambda: asyncio.run(rc2(authorization=auth_header)), 403)
check("require_role Admin blocked from SuperAdmin -> 403", ok, f"got status {st}")

ok, st = raises(lambda: asyncio.run(rc(authorization=None)), 401)
check("require_role no token -> 401", ok, f"got status {st}")

from jose import jwt as jose_jwt
from backend.core.config import settings
payload_mod = {
    "sub": "u2",
    "tenant_id": "t1",
    "role": "Employee",
    "exp": 9999999999,
}
fake_token = jose_jwt.encode(payload_mod, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
rc_admin = require_role(["Admin"])
ok, st = raises(lambda: asyncio.run(rc_admin(authorization=f"Bearer {fake_token}")), 403)
check("require_role blocks Employee from Admin-only -> 403", ok, f"got status {st}")

tid = asyncio.run(get_current_tenant_id(authorization=auth_header, x_tenant_id=None))
check("get_current_tenant_id from token", tid == "t1", f"got {tid}")

tid2 = asyncio.run(get_current_tenant_id(authorization=None, x_tenant_id="dev-tenant"))
check("get_current_tenant_id X-Tenant-ID fallback", tid2 == "dev-tenant")

ok, st = raises(lambda: asyncio.run(get_current_tenant_id(authorization="Bearer garbage", x_tenant_id="evil-tenant")), 401)
check("SECURITY FIX: invalid token + X-Tenant-ID -> 401 (no fallback)", ok, f"got status {st}")

ok, st = raises(lambda: asyncio.run(get_current_tenant_id(authorization=None, x_tenant_id=None)), 401)
check("get_current_tenant_id no info -> 401", ok)

print()
print("--- auth/schemas.py ---")
from backend.auth.schemas import LoginRequest, TokenResponse, UserInfo
from pydantic import ValidationError

lr = LoginRequest(email="a@b.com", password="x")
check("LoginRequest parses", lr.email == "a@b.com")

try:
    LoginRequest(email="not-an-email", password="x")
    check("LoginRequest rejects invalid email", False)
except ValidationError:
    check("LoginRequest rejects invalid email", True)

tr = TokenResponse(access_token="abc", expires_in=3600, refresh_token="xyz")
check("TokenResponse with extras", tr.token_type == "bearer" and tr.expires_in == 3600)

ui = UserInfo(user_id="u", role="Admin", roles=["A", "B"], email="a@b.c")
check("UserInfo parses", ui.role == "Admin" and len(ui.roles) == 2)

print()
print("--- api/v1/auth.py router ---")
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.api.v1.auth import router as auth_router

test_app = FastAPI()
test_app.include_router(auth_router, prefix="/api/v1")
tc = TestClient(test_app)

r = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "adminpass123"})
check("router login admin -> 200", r.status_code == 200, f"status={r.status_code} body={r.text}")
bt = r.json()
check("router login has access_token", "access_token" in bt and len(bt["access_token"]) > 10)
check("router login token_type=bearer", bt["token_type"] == "bearer")

r = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
check("router login wrong pw -> 401", r.status_code == 401)
r1 = tc.post("/api/v1/auth/login", json={"email": "admin@test.com", "password": "wrong"})
r2 = tc.post("/api/v1/auth/login", json={"email": "nobody@test.com", "password": "wrong"})
check("router login error identical for wrong/unknown", r1.status_code == r2.status_code and r1.json() == r2.json(),
      f"r1={r1.json()} r2={r2.json()}")

admin_tok = bt["access_token"]
r = tc.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {admin_tok}"})
check("router /me valid -> 200", r.status_code == 200, f"status={r.status_code} body={r.text}")
me = r.json()
check("router /me role=Admin", me.get("role") == "Admin", f"body={me}")
check("router /me has tenant_id", me.get("tenant_id") is not None)
check("router /me has keycloak_id key", "keycloak_id" in me)
check("router /me has roles key", "roles" in me)

r = tc.get("/api/v1/auth/me")
check("router /me no token -> 401", r.status_code == 401)

r = tc.get("/api/v1/auth/me", headers={"Authorization": "Bearer garbage"})
check("router /me garbage -> 401", r.status_code == 401)

r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {admin_tok}"})
check("router admin-only admin -> 200", r.status_code == 200)

emp_tok = tc.post("/api/v1/auth/login", json={"email": "employee@test.com", "password": "employeepass123"}).json()["access_token"]
r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {emp_tok}"})
check("router admin-only employee -> 403", r.status_code == 403)

r = tc.delete("/api/v1/auth/admin-only-test")
check("router admin-only no token -> 401", r.status_code == 401)

ta_resp = tc.post("/api/v1/auth/login", json={"email": "tenant_admin@test.com", "password": "tenantadminpass123"})
check("router login tenant_admin -> 200", ta_resp.status_code == 200, f"status={ta_resp.status_code}")
ta_tok = ta_resp.json()["access_token"]
r = tc.delete("/api/v1/auth/admin-only-test", headers={"Authorization": f"Bearer {ta_tok}"})
check("router admin-only tenant_admin -> 200", r.status_code == 200)

print()
print(f"=== TOTAL: {passed} passed, {failed} failed ===")

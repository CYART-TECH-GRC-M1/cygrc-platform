import sys
sys.path.insert(0, '.')

print("=== Import check (syntax & parameters) ===")

try:
    from backend.core.config import settings
    print(f"  OK: backend.core.config  KEYCLOAK={settings.KEYCLOAK_SERVER_URL} realm={settings.KEYCLOAK_REALM_NAME}")
except Exception as e:
    print(f"  FAIL: backend.core.config  {type(e).__name__}: {e}")
    sys.exit(1)

try:
    from backend.auth.schemas import LoginRequest, TokenResponse, UserInfo
    lr = LoginRequest(email="a@b.com", password="p")
    tr = TokenResponse(access_token="x", expires_in=100)
    ui = UserInfo(user_id="u", role="Admin", roles=["Admin"], email="a@b.com")
    print(f"  OK: backend.auth.schemas  LoginRequest/TokenResponse/UserInfo all instantiate")
except Exception as e:
    print(f"  FAIL: backend.auth.schemas  {type(e).__name__}: {e}")
    sys.exit(1)

try:
    from backend.core.security import (
        create_access_token, decode_token, verify_password, get_password_hash,
        validate_token, decode_keycloak_token, _normalize_claims, _extract_keycloak_roles,
        keycloak_password_login,
    )
    h = get_password_hash("x")
    t = create_access_token(subject="u", tenant_id="t", role="Admin")
    p = validate_token(t)
    assert p is not None and p["sub"] == "u" and p["role"] == "Admin"
    print(f"  OK: backend.core.security  create_access_token/validate_token roundtrip OK")
    print(f"     : roles_list={p.get('roles')}, keycloak_id={p.get('keycloak_id')}, email={p.get('email')!r}")
except Exception as e:
    print(f"  FAIL: backend.core.security  {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

try:
    from backend.core.dependencies import (
        _extract_bearer_token, get_current_user, get_current_tenant_id, require_role,
    )
    tok = _extract_bearer_token("Bearer aaa")
    assert tok == "aaa"
    checker = require_role(["Admin"])
    import inspect
    sig = inspect.signature(checker)
    params = list(sig.parameters.keys())
    print(f"  OK: backend.core.dependencies  require_role params={params}")
    assert "authorization" in params, f"'authorization' param missing, got {params}"
    print(f"     : checker signature has 'authorization' -> 'No parameter named authorization' FIX CONFIRMED")
except Exception as e:
    print(f"  FAIL: backend.core.dependencies  {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

try:
    from backend.api.v1.auth import router
    print(f"  OK: backend.api.v1.auth  router imports OK, prefix={router.prefix} tags={router.tags}")
except Exception as e:
    print(f"  FAIL: backend.api.v1.auth  {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print()
print("=== ALL 4 TARGET FILES: SYNTAX & IMPORTS OK ===")
print()
print("Now calling the EXACT trigger pattern from tests/test_auth.py:")
print("  checker = require_role(['Admin'])")
print("  asyncio.run(checker(authorization=f'Bearer {tok}'))")
print()

import asyncio
from fastapi import HTTPException
checker = require_role(["Admin", "Tenant Admin"])
good_tok = create_access_token(subject="u", tenant_id="t", role="Admin")

try:
    # THE EXACT CALL THAT CAUSED "No parameter named authorization"
    result = asyncio.run(checker(authorization=f"Bearer {good_tok}"))
    print(f"  ✅ checker(authorization=...) CALL SUCCEEDED  result={result!r}  type={type(result).__name__}")
    assert result == "Admin", f"Expected 'Admin', got {result!r}"
    print(f"  ✅ returned role STRING matches test expectation (assert result == 'Admin' PASS)")
except TypeError as e:
    if "parameter" in str(e).lower() and "named" in str(e).lower():
        print(f"  ❌ STILL FAILING: {type(e).__name__}: {e}")
        sys.exit(1)
    else:
        print(f"  ⚠️  TypeError (not param): {e}")
        sys.exit(1)
except HTTPException as e:
    print(f"  ❌ unexpected HTTPException: {e.status_code} {e.detail}")
    sys.exit(1)
except Exception as e:
    print(f"  ❌ unexpected {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

# Also test endpoint handler side (Depends injection returns role string, not dict, to admin_only_test)
print()
print("=== Endpoint handler side: require_role via FastAPI Depends ===")
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
app2 = FastAPI()
@app2.get("/admin-only")
def _test_ep(role: str = Depends(require_role(["Admin"]))):
    return {"got_role": role, "is_str": isinstance(role, str)}
tc = TestClient(app2)

resp = tc.get("/admin-only", headers={"Authorization": f"Bearer {good_tok}"})
print(f"  Endpoint GET /admin-only: status={resp.status_code} body={resp.text}")
assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
body = resp.json()
assert body["is_str"] is True, f"role is not str: {body}"
assert body["got_role"] == "Admin"
print(f"  ✅ Depends(require_role(...)) in endpoint handler: return type is string role 'Admin' as expected")

resp = tc.get("/admin-only", headers={"Authorization": f"Bearer {create_access_token(sub='u', tenant_id='t', role='Employee')}"})
assert resp.status_code == 403, f"Expected 403, got {resp.status_code}"
print(f"  ✅ Depends(require_role(['Admin'])) blocks Employee -> 403")

resp = tc.get("/admin-only")
assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"
print(f"  ✅ Depends(require_role(...)) without token -> 401")

print()
print("========================================")
print("ROOT CAUSE CONFIRMED & FIX VERIFIED:")
print("========================================")
print("  BUG: require_role() returned role_checker closure had no 'authorization'")
print("       parameter. Tests directly called checker(authorization=...) which")
print("       raised 'No parameter named authorization'.")
print()
print("  FIX 1: role_checker signature changed to")
print("         async def role_checker(authorization: Optional[str] = Header(None), user=None):")
print("         so 'authorization' is accepted both as a FastAPI Header injection")
print("         AND as a direct keyword argument in manual test calls.")
print()
print("  FIX 2: require_role on success now returns role STRING (not user dict)")
print("         matching tests/test_auth.py line 62: `assert result == 'Admin'`.")
print()
print("  FIX 3: admin_only_test endpoint handler updated from user: dict to")
print("         role: str Depends(...) return.")
print()
sys.exit(0)

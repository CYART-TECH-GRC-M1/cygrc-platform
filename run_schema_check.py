import sys
sys.path.insert(0, '.')

errors = []

def try_check(name, fn):
    try:
        fn()
        print(f"  OK: {name}")
    except Exception as e:
        err_msg = f"{type(e).__name__}: {e}"
        errors.append((name, err_msg, sys.exc_info()))
        print(f"  FAIL: {name} -> {err_msg[:200]}")

print("Step 1: Check Pydantic schemas in backend/auth/schemas.py")
from backend.auth.schemas import LoginRequest, TokenResponse, UserInfo
try_check("LoginRequest schema", lambda: LoginRequest.model_json_schema())
try_check("TokenResponse schema", lambda: TokenResponse.model_json_schema())
try_check("UserInfo schema", lambda: UserInfo.model_json_schema())

print("\nStep 2: Check Pydantic schemas in backend/schemas/")
from backend.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from backend.schemas.user import UserCreate, UserUpdate, UserResponse
from backend.schemas.control import (
    ControlCreate,
    ControlUpdate,
    ControlResponse,
    FrameworkCreate,
    FrameworkResponse,
)
try_check("TenantCreate", lambda: TenantCreate.model_json_schema())
try_check("TenantUpdate", lambda: TenantUpdate.model_json_schema())
try_check("TenantResponse", lambda: TenantResponse.model_json_schema())
try_check("UserCreate", lambda: UserCreate.model_json_schema())
try_check("UserUpdate", lambda: UserUpdate.model_json_schema())
try_check("UserResponse", lambda: UserResponse.model_json_schema())
try_check("ControlCreate", lambda: ControlCreate.model_json_schema())
try_check("ControlUpdate", lambda: ControlUpdate.model_json_schema())
try_check("ControlResponse", lambda: ControlResponse.model_json_schema())
try_check("FrameworkCreate", lambda: FrameworkCreate.model_json_schema())
try_check("FrameworkResponse", lambda: FrameworkResponse.model_json_schema())

print("\nStep 3: Check routers import & schema resolution by route")
from backend.api.router import api_router as v1_router
try_check("v1 router import", lambda: print(f"     routes: {len(v1_router.routes)}"))

for r in v1_router.routes:
    path = getattr(r, 'path', '')
    methods = list(getattr(r, 'methods', []) or [])
    name = getattr(r, 'name', '')
    rm = getattr(r, 'response_model', None)
    if rm is not None:
        try:
            if hasattr(rm, 'model_json_schema'):
                rm.model_json_schema()
            print(f"  OK: {methods} {path} response_model={rm.__name__}")
        except Exception as e:
            errors.append((f"route {methods} {path}", f"{type(e).__name__}: {e}", sys.exc_info()))
            print(f"  FAIL: {methods} {path} response_model={rm.__name__} -> {type(e).__name__}: {e}")

print("\nStep 4: Check main app / OpenAPI schema generation (most likely trigger)")
try:
    from backend.main import app
    openapi = app.openapi()
    print(f"  OK: OpenAPI generated successfully ({len(openapi.get('paths', {}))} paths)")
except Exception as e:
    errors.append(("OpenAPI", f"{type(e).__name__}: {e}", sys.exc_info()))
    print(f"  FAIL: OpenAPI generation -> {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print(f"TOTAL ERRORS: {len(errors)}")
for i, (name, msg, (et, ev, tb)) in enumerate(errors, 1):
    print(f"\n--- Error #{i}: {name} ---")
    print(f"  {msg}")
    print("  Stack:")
    import traceback
    traceback.print_tb(tb, limit=8)

sys.exit(0 if not errors else 1)

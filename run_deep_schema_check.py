import sys
sys.path.insert(0, '.')

print("STEP 1: import models first (warm-up)")
try:
    from backend.models.tenant import TenantStatus, Tenant
    from backend.models.user import User
    from backend.models.role import Role, UserRole
    from backend.models.control import Control, Framework
    print("  OK models")
except Exception as e:
    print(f"  FAIL models: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\nSTEP 2: schemas")
try:
    from backend.auth.schemas import LoginRequest, TokenResponse, UserInfo
    from backend.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
    from backend.schemas.user import UserCreate, UserUpdate, UserResponse
    from backend.schemas.control import ControlCreate, ControlUpdate, ControlResponse, FrameworkResponse
    print("  OK schemas imported")
except Exception as e:
    print(f"  FAIL schemas import: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

def check_schema(name, cls):
    try:
        s = cls.model_json_schema()
        print(f"    {name}: OK (refs={list(s.get('$defs', {}).keys())})")
        return True
    except Exception as e:
        print(f"    {name}: FAIL {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
        return False

all_ok = True
all_ok &= check_schema("LoginRequest", LoginRequest)
all_ok &= check_schema("TokenResponse", TokenResponse)
all_ok &= check_schema("UserInfo", UserInfo)
all_ok &= check_schema("TenantCreate", TenantCreate)
all_ok &= check_schema("TenantUpdate", TenantUpdate)
all_ok &= check_schema("TenantResponse", TenantResponse)
all_ok &= check_schema("UserCreate", UserCreate)
all_ok &= check_schema("UserUpdate", UserUpdate)
all_ok &= check_schema("UserResponse", UserResponse)
all_ok &= check_schema("ControlCreate", ControlCreate)
all_ok &= check_schema("ControlUpdate", ControlUpdate)
all_ok &= check_schema("ControlResponse", ControlResponse)
all_ok &= check_schema("FrameworkResponse", FrameworkResponse)
if not all_ok:
    sys.exit(1)

print("\nSTEP 3: security & dependencies modules")
try:
    from backend.core.dependencies import (
        _extract_bearer_token,
        get_current_user,
        get_current_tenant_id,
        require_role,
    )
    from backend.core.security import create_access_token, validate_token
    tok = create_access_token(subject="u", tenant_id="t", role="Admin")
    p = validate_token(tok)
    assert p and p["role"] == "Admin"
    checker = require_role(["Admin"])
    print(f"  OK dependencies checker params = {list(checker.__code__.co_varnames[:checker.__code__.co_argcount])}")
except Exception as e:
    print(f"  FAIL dependencies: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\nSTEP 4: routers import individually")
routers_ok = True
for name, mod in [
    ("tenants", "backend.api.v1.tenants"),
    ("users", "backend.api.v1.users"),
    ("frameworks", "backend.api.v1.frameworks"),
    ("controls", "backend.api.v1.controls"),
    ("auth", "backend.api.v1.auth"),
]:
    try:
        mod_obj = __import__(mod, fromlist=["router"])
        router = mod_obj.router
        print(f"  OK {name} router: {len(router.routes)} routes")
    except Exception as e:
        routers_ok = False
        print(f"  FAIL {name} router: {type(e).__name__}: {e}")
        import traceback; traceback.print_exc()
if not routers_ok:
    sys.exit(1)

print("\nSTEP 5: full main app + openapi generation")
try:
    from backend.main import app
    oa = app.openapi()
    n_paths = len(oa.get("paths", {}))
    print(f"  OK OpenAPI generated: {n_paths} paths")
    
    errs = []
    for p, methods in oa.get("paths", {}).items():
        for method, op in methods.items():
            if method.lower() in ("parameters", "summary", "description"):
                continue
            resp = op.get("responses", {})
            for code, rdef in resp.items():
                content = rdef.get("content", {})
                for ctype, cspec in content.items():
                    schema_ref = cspec.get("schema", {})
                    if "$ref" in schema_ref:
                        ref = schema_ref["$ref"]
                        parts = ref.split("/")
                        if len(parts) == 4 and parts[1] == "components" and parts[2] == "schemas":
                            sname = parts[3]
                            schema_def = oa.get("components", {}).get("schemas", {}).get(sname)
                            if not schema_def:
                                errs.append(f"Missing schema def: {sname} ref from {p} {method}")
                            else:
                                # Check for "Unknown" in type
                                def walk(obj, path=""):
                                    res = []
                                    if isinstance(obj, dict):
                                        if "type" in obj and obj["type"] in ("Unknown", "unknown", "UNDEFINED"):
                                            res.append(f"{path}.type={obj['type']}")
                                        if "anyOf" in obj or "oneOf" in obj or "allOf" in obj:
                                            for k in ("anyOf", "oneOf", "allOf"):
                                                if k in obj:
                                                    for i, item in enumerate(obj[k]):
                                                        res.extend(walk(item, f"{path}.{k}[{i}]"))
                                        for k, v in obj.items():
                                            res.extend(walk(v, f"{path}.{k}"))
                                    elif isinstance(obj, list):
                                        for i, item in enumerate(obj):
                                            res.extend(walk(item, f"{path}[{i}]"))
                                    return res
                                issues = walk(schema_def, f"components.schemas.{sname}")
                                for i in issues:
                                    errs.append(i)
                    elif "anyOf" in schema_ref:
                        # Check anyOf for "Unknown" as first element
                        for i, item in enumerate(schema_ref["anyOf"]):
                            t = item.get("type") if isinstance(item, dict) else None
                            if t == "Unknown":
                                errs.append(f"{p} {method} response anyOf[{i}] -> type=Unknown at {code} {ctype}")
    
    if errs:
        print(f"  WARNINGS/ISSUES: {len(errs)}")
        for e in errs[:30]:
            print(f"    - {e}")
    else:
        print("  OK: No 'Unknown' type found in OpenAPI schemas.")
    
    # Also check all endpoint response_model types print type annotations
    import inspect
    for r in app.routes:
        if hasattr(r, 'endpoint') and r.endpoint is not None:
            sig = inspect.signature(r.endpoint)
            ret = sig.return_annotation
            path = getattr(r, 'path', '?')
            methods = list(getattr(r, 'methods', ['?']) or ['?'])
            # Skip type annotation = inspect.Parameter.empty, that's fine
            if ret is not inspect.Parameter.empty:
                # Check if it contains "Unknown" text when stringified
                ret_s = str(ret)
                if "Unknown" in ret_s:
                    print(f"    ⚠️  Endpoint return annotation with 'Unknown' -> {methods} {path}: {ret_s}")
except Exception as e:
    print(f"  FAIL OpenAPI: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
    sys.exit(1)

print("\n=== DONE ===")

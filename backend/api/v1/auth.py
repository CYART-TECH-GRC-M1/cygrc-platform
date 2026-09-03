"""
TEMPORARY LOCAL AUTH — placeholder until Keycloak integration is confirmed.

The `users` table has no password column (schema.sql), which indicates
production auth is meant to flow through Keycloak. Until that's wired up
(Team E) and the team confirms the approach, this endpoint authenticates
against a small hardcoded test-user set so the rest of the team can build
and test against a working /auth/login and get real JWTs.

TODO: Replace with Keycloak token validation once ready.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any, Dict, Optional

from backend.auth.schemas import LoginRequest, TokenResponse, UserInfo
from backend.core.config import settings
from backend.core.dependencies import get_current_user, require_role
from backend.core.security import (
    create_access_token,
    get_password_hash,
    keycloak_password_login,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_LOCAL_USERS = {
    "admin@test.com": {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "tenant_id": "00000000-0000-0000-0000-00000000000a",
        "role": "Admin",
        "hashed_password": get_password_hash("adminpass123"),
    },
    "tenant_admin@test.com": {
        "user_id": "00000000-0000-0000-0000-000000000003",
        "tenant_id": "00000000-0000-0000-0000-00000000000a",
        "role": "Tenant Admin",
        "hashed_password": get_password_hash("tenantadminpass123"),
    },
    "employee@test.com": {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "tenant_id": "00000000-0000-0000-0000-00000000000a",
        "role": "Employee",
        "hashed_password": get_password_hash("employeepass123"),
    },
}

_UNAUTH_MSG = "Incorrect email or password."


async def _try_keycloak_login(payload: LoginRequest) -> Optional[TokenResponse]:
    kc_resp = await keycloak_password_login(payload.email, payload.password)
    if not kc_resp:
        return None

    access_token = kc_resp.get("access_token")
    if not access_token:
        return None

    return TokenResponse(
        access_token=access_token,
        token_type=kc_resp.get("token_type", "bearer"),
        expires_in=kc_resp.get("expires_in"),
        refresh_token=kc_resp.get("refresh_token"),
    )


def _try_local_login(payload: LoginRequest) -> Optional[TokenResponse]:
    user = _LOCAL_USERS.get(payload.email)
    if not user or not verify_password(payload.password, user["hashed_password"]):
        return None

    token = create_access_token(
        subject=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest) -> TokenResponse:
    kc_result = await _try_keycloak_login(payload)
    if kc_result is not None:
        return kc_result

    if settings.LOCAL_AUTH_ENABLED or not settings.KEYCLOAK_ENABLED:
        local_result = _try_local_login(payload)
        if local_result is not None:
            return local_result

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=_UNAUTH_MSG,
        headers={"WWW-Authenticate": "Bearer"},
    )


@router.get("/me", response_model=UserInfo)
async def whoami(user: Dict[str, Any] = Depends(get_current_user)) -> UserInfo:
    return UserInfo(
        user_id=user.get("user_id"),
        keycloak_id=user.get("keycloak_id"),
        tenant_id=user.get("tenant_id"),
        role=user.get("role"),
        email=user.get("email"),
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        roles=user.get("roles", []),
    )


@router.delete("/admin-only-test")
async def admin_only_test(
    role: str = Depends(require_role(["Admin", "Tenant Admin"])),
) -> Dict[str, Any]:
    return {"message": f"Access granted to role '{role}'."}

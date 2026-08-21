from typing import Optional
from fastapi import Header, HTTPException, status
from backend.core.security import decode_token


async def get_current_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    authorization: Optional[str] = Header(None)
) -> str:
    # 1. Check if token provided in Authorization header
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        payload = decode_token(token)
        if payload and "tenant_id" in payload:
            return payload["tenant_id"]

    # 2. Fallback to X-Tenant-ID header for dev/testing
    if x_tenant_id:
        return x_tenant_id

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Tenant identity could not be verified. Provide 'Authorization' Bearer token or 'X-Tenant-ID' header."
    )


def require_role(allowed_roles: list[str]):
    async def role_checker(
        authorization: Optional[str] = Header(None)
    ) -> str:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid Authorization header."
            )

        token = authorization.split(" ")[1]
        payload = decode_token(token)

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token."
            )

        role = payload.get("role")
        if role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' is not permitted to access this resource."
            )

        return role

    return role_checker

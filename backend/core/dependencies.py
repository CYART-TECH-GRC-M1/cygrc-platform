from typing import Any, Callable, Dict, List, Optional

from fastapi import Depends, Header, HTTPException, status

from backend.core.security import validate_token


BEARER_PREFIX = "Bearer"


def unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise unauthorized("Missing Authorization header.")

    parts = authorization.strip().split(" ", 1)
    if len(parts) != 2:
        raise unauthorized(
            "Invalid Authorization header format. Expected 'Bearer <token>'."
        )

    scheme, token = parts
    if scheme.lower() != BEARER_PREFIX.lower():
        raise unauthorized(
            "Invalid authentication scheme. Expected Bearer authentication."
        )

    token = token.strip()
    if not token:
        raise unauthorized("Bearer token is missing.")

    return token


async def get_current_user(
    authorization: Optional[str] = Header(
        default=None,
        alias="Authorization",
    ),
) -> Dict[str, Any]:
    token = _extract_bearer_token(authorization)

    try:
        payload = validate_token(token)
    except Exception:
        raise unauthorized("Invalid or expired token.")

    if not payload or not isinstance(payload, dict):
        raise unauthorized("Invalid or expired token.")

    user_id = payload.get("sub")
    keycloak_id = payload.get("keycloak_id")
    tenant_id = payload.get("tenant_id")
    role = payload.get("role")
    email = payload.get("email")
    first_name = payload.get("first_name")
    last_name = payload.get("last_name")

    roles = payload.get("roles", [])
    if roles is None:
        roles = []
    if isinstance(roles, str):
        roles = [roles]
    if not isinstance(roles, list):
        roles = []
    roles = [
        r.strip()
        for r in roles
        if isinstance(r, str) and r.strip()
    ]

    if isinstance(role, str):
        role = role.strip() or None
    else:
        role = None

    if not user_id:
        raise unauthorized("Token does not contain a valid user identity.")

    return {
        "user_id": user_id,
        "keycloak_id": keycloak_id,
        "tenant_id": tenant_id,
        "role": role,
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "roles": roles,
    }


async def get_current_tenant_id(
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
    authorization: Optional[str] = Header(None),
) -> str:
    if authorization:
        user = await get_current_user(authorization)

        tenant_id = user.get("tenant_id")

        if not tenant_id:
            raise unauthorized("Token does not contain a tenant_id claim.")

        if not isinstance(tenant_id, str):
            raise unauthorized("Invalid tenant_id claim.")

        tenant_id = tenant_id.strip()
        if not tenant_id:
            raise unauthorized("Token contains an empty tenant_id claim.")

        return tenant_id

    if x_tenant_id:
        tenant_id = x_tenant_id.strip()
        if tenant_id:
            return tenant_id

    raise unauthorized(
        "Tenant identity could not be verified. "
        "Provide an Authorization Bearer token or X-Tenant-ID header."
    )


def require_role(
    allowed_roles: List[str],
) -> Callable:
    if not allowed_roles:
        raise ValueError("allowed_roles must contain at least one role.")

    normalized_allowed_roles = {
        role.strip().lower()
        for role in allowed_roles
        if isinstance(role, str) and role.strip()
    }

    if not normalized_allowed_roles:
        raise ValueError("allowed_roles must contain valid role names.")

    async def role_checker(
        user: Optional[Dict[str, Any]] = Depends(get_current_user),
        authorization: Optional[str] = Header(
            default=None,
            alias="Authorization",
        ),
    ) -> str:
        if not isinstance(user, dict):
            if authorization is None:
                raise unauthorized("Missing Authorization header.")
            user = await get_current_user(authorization=authorization)

        if not isinstance(user, dict):
            raise unauthorized("Invalid authenticated user information.")

        primary_role = user.get("role")
        if isinstance(primary_role, str):
            primary_role = primary_role.strip()
        else:
            primary_role = None

        if primary_role and primary_role.lower() in normalized_allowed_roles:
            return primary_role

        user_roles = user.get("roles", [])
        if not isinstance(user_roles, list):
            user_roles = []

        for user_role in user_roles:
            if not isinstance(user_role, str):
                continue
            user_role = user_role.strip()
            if not user_role:
                continue
            if user_role.lower() in normalized_allowed_roles:
                return user_role

        displayed_role = primary_role or "none"
        raise forbidden(
            f"Role '{displayed_role}' is not permitted to access this resource. "
            f"Allowed roles: {', '.join(sorted(normalized_allowed_roles))}"
        )

    return role_checker

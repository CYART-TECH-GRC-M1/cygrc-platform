from typing import Any, Callable, Dict, List, Optional, Union

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer

from backend.core.config import settings
from backend.core.permissions import (
    Permission,
    has_permission,
    normalize_role_name,
)
from backend.core.security import validate_token


BEARER_PREFIX = "Bearer"
bearer_scheme = HTTPBearer(auto_error=False)


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
    x_tenant_id: Optional[str] = Header(
        default=None,
        alias="X-Tenant-ID",
    ),
    bearer_credentials=Depends(bearer_scheme),
) -> Dict[str, Any]:
    if not authorization and bearer_credentials:
        authorization = f"Bearer {bearer_credentials.credentials}"

    if not authorization:
        if settings.is_production() or not settings.is_dev_tenant_header_allowed:
            raise unauthorized("Missing Authorization header.")
        if x_tenant_id and x_tenant_id.strip():
            return {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "keycloak_id": None,
                "tenant_id": x_tenant_id.strip(),
                "role": "Super Admin",
                "email": "dev-admin@cygrc.local",
                "first_name": "Dev",
                "last_name": "Admin",
                "roles": ["Super Admin"],
            }
        raise unauthorized("Missing Authorization header.")

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
    bearer_credentials=Depends(bearer_scheme),
) -> str:
    if not authorization and bearer_credentials:
        authorization = f"Bearer {bearer_credentials.credentials}"

    if authorization:
        user = await get_current_user(
            authorization=authorization,
            x_tenant_id=x_tenant_id,
            bearer_credentials=bearer_credentials,
        )

        token_tenant_id = user.get("tenant_id")

        if not token_tenant_id:
            raise unauthorized("Token does not contain a tenant_id claim.")

        if not isinstance(token_tenant_id, str):
            raise unauthorized("Invalid tenant_id claim.")

        token_tenant_id = token_tenant_id.strip()
        if not token_tenant_id:
            raise unauthorized("Token contains an empty tenant_id claim.")

        # If client also supplied an X-Tenant-ID header, verify it matches token
        # unless caller has super-admin or platform-operator role
        if x_tenant_id:
            header_tenant_id = x_tenant_id.strip()
            all_user_roles = [user.get("role")] + user.get("roles", [])
            user_roles = [normalize_role_name(r) for r in all_user_roles if r]
            is_platform_admin = any(
                r in {"super admin", "platform operator", "admin"} for r in user_roles
            )
            if not is_platform_admin and header_tenant_id != token_tenant_id:
                raise forbidden("Cross-tenant access forbidden: X-Tenant-ID does not match authenticated token.")
            if is_platform_admin and header_tenant_id:
                return header_tenant_id

        return token_tenant_id

    # If no Authorization header is provided:
    if settings.is_production():
        raise unauthorized(
            "Authentication token required. Unauthenticated client tenant headers are strictly rejected in production."
        )

    if settings.is_dev_tenant_header_allowed and x_tenant_id:
        tenant_id = x_tenant_id.strip()
        if tenant_id:
            return tenant_id

    raise unauthorized(
        "Tenant identity could not be verified. Provide an Authorization Bearer token."
    )


def require_role(
    allowed_roles: List[str],
) -> Callable:
    if not allowed_roles:
        raise ValueError("allowed_roles must contain at least one role.")

    normalized_allowed_roles = {
        normalize_role_name(role)
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
        user_roles = user.get("roles", [])
        if not isinstance(user_roles, list):
            user_roles = []
        if primary_role:
            user_roles = [primary_role] + user_roles

        normalized_user_roles = {normalize_role_name(r) for r in user_roles if r}

        # Platform Operator / Super Admin / Admin has universal role access
        if any(r in {"super admin", "platform operator", "admin"} for r in normalized_user_roles):
            return primary_role or "Admin"

        matched = normalized_user_roles.intersection(normalized_allowed_roles)
        if matched:
            return next(iter(matched))

        displayed_role = primary_role or "none"
        raise forbidden(
            f"Role '{displayed_role}' is not permitted to access this resource. "
            f"Allowed roles: {', '.join(sorted(normalized_allowed_roles))}"
        )

    return role_checker


def require_permission(
    permission: Union[Permission, str],
) -> Callable:
    async def permission_checker(
        user: Optional[Dict[str, Any]] = Depends(get_current_user),
        authorization: Optional[str] = Header(
            default=None,
            alias="Authorization",
        ),
    ) -> Dict[str, Any]:
        if not isinstance(user, dict):
            if authorization is None:
                raise unauthorized("Missing Authorization header.")
            user = await get_current_user(authorization=authorization)

        primary_role = user.get("role")
        user_roles = user.get("roles", [])
        if not isinstance(user_roles, list):
            user_roles = []
        if primary_role:
            user_roles = [primary_role] + user_roles

        if not has_permission(user_roles, permission):
            perm_str = permission.value if isinstance(permission, Permission) else str(permission)
            raise forbidden(
                f"Missing required permission '{perm_str}'. Access denied."
            )
        return user

    return permission_checker

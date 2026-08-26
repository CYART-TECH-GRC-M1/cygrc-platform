"""
TEMPORARY LOCAL AUTH — placeholder until Keycloak integration is confirmed.

The `users` table has no password column (schema.sql), which indicates
production auth is meant to flow through Keycloak. Until that's wired up
(Team E) and the team confirms the approach, this endpoint authenticates
against a small hardcoded test-user set so the rest of the team can build
and test against a working /auth/login and get real JWTs.

TODO: Replace with Keycloak token validation once ready.
"""
from fastapi import APIRouter, HTTPException, status
from backend.auth.schemas import LoginRequest, TokenResponse
from backend.core.security import verify_password, get_password_hash, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

# Temporary in-memory test users. NOT the real `users` table.
_TEST_USERS = {
    "admin@test.com": {
        "user_id": "00000000-0000-0000-0000-000000000001",
        "tenant_id": "00000000-0000-0000-0000-00000000000a",
        "role": "Admin",
        "hashed_password": get_password_hash("adminpass123"),
    },
    "employee@test.com": {
        "user_id": "00000000-0000-0000-0000-000000000002",
        "tenant_id": "00000000-0000-0000-0000-00000000000a",
        "role": "Employee",
        "hashed_password": get_password_hash("employeepass123"),
    },
}


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    user = _TEST_USERS.get(payload.email)

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    token = create_access_token(
        subject=user["user_id"],
        tenant_id=user["tenant_id"],
        role=user["role"],
    )
    return TokenResponse(access_token=token)

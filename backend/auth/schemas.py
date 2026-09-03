from pydantic import BaseModel, EmailStr
from typing import List, Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None


class UserInfo(BaseModel):
    user_id: Optional[str] = None
    keycloak_id: Optional[str] = None
    tenant_id: Optional[str] = None
    role: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    roles: Optional[List[str]] = None

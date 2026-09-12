from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from backend.models.tenant import TenantStatus


class UserBase(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    keycloak_id: Optional[str] = None
    status: Optional[TenantStatus] = TenantStatus.ACTIVE


class UserCreate(BaseModel):
<<<<<<< HEAD
    # tenant_id is intentionally NOT accepted here — it's always derived
    # from the authenticated caller's tenant to enforce zero-trust isolation.
=======
    tenant_id: Optional[UUID] = None
>>>>>>> origin/Abhishek
    first_name: str
    last_name: Optional[str] = None
    email: EmailStr
    keycloak_id: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    status: Optional[TenantStatus] = None


class UserResponse(UserBase):
    user_id: UUID
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

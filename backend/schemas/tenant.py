from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID
from backend.models.tenant import TenantStatus


class TenantBase(BaseModel):
    name: str
    domain: Optional[str] = None
    subscription_plan: Optional[str] = "FREE"
    status: Optional[TenantStatus] = TenantStatus.ACTIVE


class TenantCreate(BaseModel):
    name: str
    domain: Optional[str] = None
    subscription_plan: Optional[str] = "FREE"


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    subscription_plan: Optional[str] = None
    status: Optional[TenantStatus] = None


class TenantResponse(TenantBase):
    tenant_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

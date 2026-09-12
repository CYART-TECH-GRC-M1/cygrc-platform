from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class FrameworkResponse(BaseModel):
    framework_id: UUID
    framework_name: str
    version: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ControlResponse(BaseModel):
    control_id: UUID
    framework_id: UUID
    control_code: str
    control_name: str
    description: Optional[str] = None
    status: Optional[str] = "ACTIVE"
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ControlCreate(BaseModel):
    framework_id: UUID
    control_code: str = Field(..., min_length=1, max_length=50)
    control_name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(default="ACTIVE", max_length=50)


class ControlUpdate(BaseModel):
    control_code: Optional[str] = Field(default=None, max_length=50)
    control_name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, max_length=50)


class ProvisionSummary(BaseModel):
    tenant_id: UUID
    frameworks_seeded: List[str]
    mappings_created: int
    mappings_skipped: int

    model_config = ConfigDict(from_attributes=True)


class TenantMappedControlResponse(BaseModel):
    mapping_id: UUID
    tenant_id: UUID
    control_id: UUID
    mapping_status: Optional[str] = None
    seeded_at: Optional[datetime] = None
    control_code: str
    control_name: str
    description: Optional[str] = None
    control_status: Optional[str] = None
    framework_id: UUID
    framework_name: str
    framework_version: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

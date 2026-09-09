from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


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

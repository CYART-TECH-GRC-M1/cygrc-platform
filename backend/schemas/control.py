from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FrameworkResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str = "compliance"
    is_default: bool = True


class ControlResponse(BaseModel):
    id: int
    tenant_id: str
    framework_id: int
    name: str
    description: Optional[str] = None
    status: str = "active"
    owner: Optional[str] = None


class ControlCreate(BaseModel):
    framework_id: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: str = Field(default="active", min_length=1, max_length=50)
    owner: Optional[str] = Field(default=None, max_length=120)


class ControlUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(default=None, min_length=1, max_length=50)
    owner: Optional[str] = Field(default=None, max_length=120)

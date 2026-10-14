from typing import Optional
from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class EvidenceCreate(BaseModel):
    control_id: uuid.UUID
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    status: Optional[str] = "ACTIVE"


class EvidenceResponse(BaseModel):
    evidence_id: uuid.UUID
    tenant_id: uuid.UUID
    control_id: uuid.UUID
    uploaded_by: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


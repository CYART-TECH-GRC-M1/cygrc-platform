from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.dfir import CustodyAction


class CustodyCreate(BaseModel):
    action: CustodyAction
    source: str | None = Field(default=None, max_length=255)
    destination: str | None = Field(default=None, max_length=255)
    notes: str | None = None
    integrity_hash: str | None = Field(default=None, max_length=128)


class CustodyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    custody_id: UUID
    tenant_id: UUID
    evidence_id: UUID
    performed_by: UUID
    action: CustodyAction
    source: str | None = None
    destination: str | None = None
    notes: str | None = None
    integrity_hash: str | None = None
    timestamp: datetime

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.models.tenant import TenantStatus


class EvidenceUploadResponse(BaseModel):
    evidence_id: UUID
    tenant_id: UUID
    control_id: UUID
    requirement_id: Optional[UUID] = None
    title: str
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    sha256: str
    blob_s3_key: str
    uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceDetailResponse(EvidenceUploadResponse):
    uploaded_by: UUID
    description: Optional[str] = None
    content_type: Optional[str] = None
    status: Optional[TenantStatus] = None


class EvidenceVerifyResponse(BaseModel):
    evidence_id: UUID
    stored_sha256: str
    computed_sha256: str
    intact: bool

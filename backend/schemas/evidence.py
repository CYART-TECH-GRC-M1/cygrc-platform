from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.models.evidence import ReviewStatus
from backend.models.tenant import TenantStatus


class EvidenceFileResponse(BaseModel):
    file_id: UUID
    evidence_id: UUID
    file_name: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceFileUploadResponse(EvidenceFileResponse):
    sha256: str


class EvidenceReviewResponse(BaseModel):
    review_id: UUID
    evidence_id: UUID
    reviewer_id: UUID
    review_status: Optional[ReviewStatus] = None
    comments: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceReviewCreate(BaseModel):
    review_status: ReviewStatus
    comments: Optional[str] = None


class EvidenceCreate(BaseModel):
    control_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class EvidenceUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TenantStatus] = None


class EvidenceResponse(BaseModel):
    evidence_id: UUID
    tenant_id: UUID
    control_id: UUID
    uploaded_by: UUID
    title: str
    description: Optional[str] = None
    status: Optional[TenantStatus] = None
    uploaded_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class EvidenceDetailResponse(EvidenceResponse):
    files: List[EvidenceFileResponse] = []
    reviews: List[EvidenceReviewResponse] = []

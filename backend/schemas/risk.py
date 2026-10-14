from typing import Optional, List
from datetime import datetime, date
import uuid
from pydantic import BaseModel, Field


class RiskCreate(BaseModel):
    title: str = Field(..., max_length=255)
    description: Optional[str] = None
    control_id: Optional[uuid.UUID] = None
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = "ACTIVE"


class RiskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    control_id: Optional[uuid.UUID] = None
    likelihood: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None


class RiskResponse(BaseModel):
    risk_id: uuid.UUID
    tenant_id: uuid.UUID
    control_id: Optional[uuid.UUID] = None
    title: str
    description: Optional[str] = None
    likelihood: Optional[int] = None
    impact: Optional[int] = None
    risk_score: Optional[int] = None
    status: str
    created_by: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentCreate(BaseModel):
    likelihood: int = Field(..., ge=1, le=5)
    impact: int = Field(..., ge=1, le=5)
    comments: Optional[str] = None


class RiskAssessmentResponse(BaseModel):
    assessment_id: uuid.UUID
    risk_id: uuid.UUID
    assessor_id: uuid.UUID
    assessment_date: date
    likelihood: int
    impact: int
    risk_score: int
    comments: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RiskTreatmentCreate(BaseModel):
    treatment_plan: str
    owner_id: Optional[uuid.UUID] = None
    target_date: Optional[date] = None
    status: Optional[str] = "OPEN"


class RiskTreatmentResponse(BaseModel):
    treatment_id: uuid.UUID
    risk_id: uuid.UUID
    owner_id: Optional[uuid.UUID] = None
    treatment_plan: str
    target_date: Optional[date] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


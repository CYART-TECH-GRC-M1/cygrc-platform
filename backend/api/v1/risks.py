import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.risk import RiskRegister, RiskAssessment, RiskTreatment

router = APIRouter()


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class RiskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    likelihood: int  # 1-5
    impact: int      # 1-5
    status: str = "ACTIVE"
    source: str = "MANUAL"


class RiskAssessmentCreate(BaseModel):
    likelihood: int
    impact: int
    comments: Optional[str] = None


class RiskTreatmentCreate(BaseModel):
    treatment_plan: str
    status: str = "OPEN"


class RiskResponse(BaseModel):
    risk_id: str
    tenant_id: str
    title: str
    description: Optional[str] = None
    likelihood: int
    impact: int
    risk_score: int
    status: str
    source: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RiskAssessmentResponse(BaseModel):
    assessment_id: str
    risk_id: str
    likelihood: int
    impact: int
    risk_score: int
    comments: Optional[str] = None
    assessed_at: datetime

    class Config:
        from_attributes = True


class RiskTreatmentResponse(BaseModel):
    treatment_id: str
    risk_id: str
    treatment_plan: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    payload: RiskCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new risk register entry for the tenant."""
    risk_score = payload.likelihood * payload.impact
    risk = RiskRegister(
        tenant_id=tenant_id,
        title=payload.title,
        description=payload.description,
        likelihood=payload.likelihood,
        impact=payload.impact,
        risk_score=risk_score,
        status=payload.status.upper(),
        source=payload.source,
    )
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    # Serialize UUID fields
    return _risk_to_dict(risk)


@router.get("", response_model=List[RiskResponse])
async def list_risks(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """List all risks for the tenant."""
    stmt = select(RiskRegister).where(RiskRegister.tenant_id == tenant_id).order_by(RiskRegister.created_at.desc())
    result = await db.execute(stmt)
    risks = result.scalars().all()
    return [_risk_to_dict(r) for r in risks]


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific risk by ID."""
    risk = await _get_risk_or_404(risk_id, tenant_id, db)
    return _risk_to_dict(risk)


@router.post("/{risk_id}/assessments", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_assessment(
    risk_id: str,
    payload: RiskAssessmentCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Record a new assessment for an existing risk, updating its score."""
    risk = await _get_risk_or_404(risk_id, tenant_id, db)

    new_score = payload.likelihood * payload.impact

    assessment = RiskAssessment(
        risk_id=risk.risk_id,
        likelihood=payload.likelihood,
        impact=payload.impact,
        risk_score=new_score,
        comments=payload.comments,
    )
    # Update the parent risk to reflect latest assessment
    risk.likelihood = payload.likelihood
    risk.impact = payload.impact
    risk.risk_score = new_score
    risk.updated_at = datetime.utcnow()

    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)

    return {
        "assessment_id": str(assessment.assessment_id),
        "risk_id": str(assessment.risk_id),
        "likelihood": assessment.likelihood,
        "impact": assessment.impact,
        "risk_score": assessment.risk_score,
        "comments": assessment.comments,
        "assessed_at": assessment.assessed_at,
    }


@router.post("/{risk_id}/treatments", response_model=RiskTreatmentResponse, status_code=status.HTTP_201_CREATED)
async def create_risk_treatment(
    risk_id: str,
    payload: RiskTreatmentCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Attach a treatment / remediation plan to a risk."""
    risk = await _get_risk_or_404(risk_id, tenant_id, db)

    treatment = RiskTreatment(
        risk_id=risk.risk_id,
        treatment_plan=payload.treatment_plan,
        status=payload.status.upper(),
    )
    db.add(treatment)
    await db.commit()
    await db.refresh(treatment)

    return {
        "treatment_id": str(treatment.treatment_id),
        "risk_id": str(treatment.risk_id),
        "treatment_plan": treatment.treatment_plan,
        "status": treatment.status,
        "created_at": treatment.created_at,
        "updated_at": treatment.updated_at,
    }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _get_risk_or_404(risk_id: str, tenant_id: str, db: AsyncSession) -> RiskRegister:
    stmt = select(RiskRegister).where(
        RiskRegister.risk_id == uuid.UUID(risk_id),
        RiskRegister.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    risk = result.scalar_one_or_none()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


def _risk_to_dict(risk: RiskRegister) -> dict:
    return {
        "risk_id": str(risk.risk_id),
        "tenant_id": str(risk.tenant_id),
        "title": risk.title,
        "description": risk.description,
        "likelihood": risk.likelihood,
        "impact": risk.impact,
        "risk_score": risk.risk_score,
        "status": risk.status,
        "source": risk.source,
        "created_at": risk.created_at,
        "updated_at": risk.updated_at,
    }

from typing import List, Optional, Any
import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id, get_current_user
from backend.schemas.risk import (
    RiskCreate,
    RiskUpdate,
    RiskResponse,
    RiskAssessmentCreate,
    RiskAssessmentResponse,
    RiskTreatmentCreate,
    RiskTreatmentResponse,
)
from backend.services.risk_service import RiskService

router = APIRouter()


def _ensure_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        # Fallback deterministic uuid for testing
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))


from typing import Any


@router.post("", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    payload: RiskCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new risk in the Risk Register."""
    t_id = _ensure_uuid(tenant_id)
    u_id = _ensure_uuid(getattr(current_user, "user_id", None) or getattr(current_user, "id", None) or uuid.uuid4())
    return await RiskService.create_risk(db=db, tenant_id=t_id, payload=payload, created_by=u_id)


@router.get("", response_model=List[RiskResponse])
async def list_risks(
    control_id: Optional[uuid.UUID] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """List all risks for the current tenant."""
    t_id = _ensure_uuid(tenant_id)
    return await RiskService.list_risks(db=db, tenant_id=t_id, control_id=control_id)


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve details for a specific risk."""
    t_id = _ensure_uuid(tenant_id)
    return await RiskService.get_risk(db=db, tenant_id=t_id, risk_id=risk_id)


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: uuid.UUID,
    payload: RiskUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Update risk metadata, likelihood, impact, or status."""
    t_id = _ensure_uuid(tenant_id)
    return await RiskService.update_risk(db=db, tenant_id=t_id, risk_id=risk_id, payload=payload)


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(
    risk_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Delete a risk from the tenant's register."""
    t_id = _ensure_uuid(tenant_id)
    await RiskService.delete_risk(db=db, tenant_id=t_id, risk_id=risk_id)


@router.post("/{risk_id}/assessments", response_model=RiskAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def add_risk_assessment(
    risk_id: uuid.UUID,
    payload: RiskAssessmentCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record an assessment for a risk and recalculate risk score."""
    t_id = _ensure_uuid(tenant_id)
    u_id = _ensure_uuid(getattr(current_user, "user_id", None) or getattr(current_user, "id", None) or uuid.uuid4())
    return await RiskService.add_assessment(
        db=db,
        tenant_id=t_id,
        risk_id=risk_id,
        payload=payload,
        assessor_id=u_id,
    )


@router.post("/{risk_id}/treatments", response_model=RiskTreatmentResponse, status_code=status.HTTP_201_CREATED)
async def add_risk_treatment(
    risk_id: uuid.UUID,
    payload: RiskTreatmentCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Add a risk treatment plan (mitigation action)."""
    t_id = _ensure_uuid(tenant_id)
    return await RiskService.add_treatment(
        db=db,
        tenant_id=t_id,
        risk_id=risk_id,
        payload=payload,
    )


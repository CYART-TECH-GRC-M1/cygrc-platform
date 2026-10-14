from typing import List, Optional, Any
import uuid
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id, get_current_user
from backend.schemas.evidence import EvidenceCreate, EvidenceResponse
from backend.services.evidence_service import EvidenceService

router = APIRouter()


def _ensure_uuid(val: Any) -> uuid.UUID:
    if isinstance(val, uuid.UUID):
        return val
    try:
        return uuid.UUID(str(val))
    except (ValueError, TypeError):
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(val))


@router.post("", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    payload: EvidenceCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Any = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Attach a new piece of evidence to a compliance control."""
    t_id = _ensure_uuid(tenant_id)
    u_id = _ensure_uuid(getattr(current_user, "user_id", None) or getattr(current_user, "id", None) or uuid.uuid4())
    return await EvidenceService.create_evidence(db=db, tenant_id=t_id, uploaded_by=u_id, payload=payload)


@router.get("", response_model=List[EvidenceResponse])
async def list_evidence(
    control_id: Optional[uuid.UUID] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """List compliance evidence for the tenant, optionally filtered by control_id."""
    t_id = _ensure_uuid(tenant_id)
    return await EvidenceService.list_evidence(db=db, tenant_id=t_id, control_id=control_id)


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: uuid.UUID,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Get single evidence record details."""
    t_id = _ensure_uuid(tenant_id)
    return await EvidenceService.get_evidence(db=db, tenant_id=t_id, evidence_id=evidence_id)


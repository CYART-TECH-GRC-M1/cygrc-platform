from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.stix_object import StixObject
from backend.services.stix_validator import STIXValidator, STIXValidationError

router = APIRouter()


class StixObjectCreate(BaseModel):
    stix_id: Optional[str] = None
    type: str  # indicator, malware, threat-actor, vulnerability, etc.
    spec_version: str = "2.1"
    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    pattern_type: Optional[str] = "stix"
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    revoked: Optional[bool] = False
    source: Optional[str] = None
    labels: Optional[List[str]] = []
    confidence: Optional[int] = 50
    raw_stix: Optional[Dict[str, Any]] = None


class StixObjectResponse(BaseModel):
    stix_id: str
    tenant_id: Optional[str] = None
    type: str
    spec_version: str
    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    pattern_type: Optional[str] = "stix"
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    revoked: Optional[bool] = False
    source: Optional[str] = None
    labels: Optional[List[str]] = []
    confidence: Optional[int] = 50
    raw_stix: Optional[Dict[str, Any]] = None
    created_at: datetime
    modified_at: datetime

    class Config:
        from_attributes = True


@router.post("/objects", response_model=StixObjectResponse, status_code=status.HTTP_201_CREATED)
async def store_stix_object(
    payload: StixObjectCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Store or update a validated STIX 2.1 object with strict tenant isolation."""
    # 1. Validate STIX 2.1 specification constraints
    try:
        norm_type = STIXValidator.validate_object_type(payload.type)
        spec_ver = STIXValidator.validate_spec_version(payload.spec_version)
        confidence = STIXValidator.validate_confidence(payload.confidence)
        STIXValidator.validate_pattern(
            pattern=payload.pattern,
            pattern_type=payload.pattern_type or "stix",
            obj_type=norm_type,
        )
        STIXValidator.validate_timestamps(
            valid_from=payload.valid_from,
            valid_until=payload.valid_until,
        )
        if payload.stix_id:
            STIXValidator.validate_stix_id(payload.stix_id, expected_type=norm_type)
    except STIXValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"STIX 2.1 validation failure: {str(err)}"
        )

    # 2. Determine target STIX ID
    object_id = payload.stix_id or f"{norm_type}--{uuid.uuid4()}"

    # 3. Handle cross-tenant collisions safely
    # Check if object exists for THIS tenant
    stmt_this_tenant = select(StixObject).where(
        StixObject.stix_id == object_id,
        StixObject.tenant_id == tenant_id,
    )
    existing_this_tenant = (await db.execute(stmt_this_tenant)).scalar_one_or_none()

    if not existing_this_tenant:
        # Check if the exact stix_id exists for a DIFFERENT tenant
        stmt_other = select(StixObject).where(
            StixObject.stix_id == object_id,
            StixObject.tenant_id != tenant_id,
        )
        other_exists = (await db.execute(stmt_other)).scalar_one_or_none()
        if other_exists:
            # Deterministically scope with tenant prefix to avoid overwriting or collision
            tenant_prefix = tenant_id[:8]
            if f"-{tenant_prefix}" not in object_id:
                object_id = f"{object_id}-{tenant_prefix}"

    if existing_this_tenant:
        existing_this_tenant.name = payload.name
        existing_this_tenant.description = payload.description
        existing_this_tenant.pattern = payload.pattern
        existing_this_tenant.pattern_type = payload.pattern_type or "stix"
        existing_this_tenant.valid_from = payload.valid_from
        existing_this_tenant.valid_until = payload.valid_until
        existing_this_tenant.revoked = bool(payload.revoked)
        existing_this_tenant.source = payload.source
        existing_this_tenant.labels = payload.labels or []
        existing_this_tenant.confidence = confidence
        existing_this_tenant.raw_stix = payload.raw_stix or {}
        existing_this_tenant.modified_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing_this_tenant)
        return existing_this_tenant

    stix_obj = StixObject(
        stix_id=object_id,
        tenant_id=tenant_id,
        type=norm_type,
        spec_version=spec_ver,
        name=payload.name,
        description=payload.description,
        pattern=payload.pattern,
        pattern_type=payload.pattern_type or "stix",
        valid_from=payload.valid_from,
        valid_until=payload.valid_until,
        revoked=bool(payload.revoked),
        source=payload.source,
        labels=payload.labels or [],
        confidence=confidence,
        raw_stix=payload.raw_stix or {},
    )
    db.add(stix_obj)
    await db.commit()
    await db.refresh(stix_obj)
    return stix_obj


@router.get("/objects", response_model=List[StixObjectResponse])
async def list_stix_objects(
    object_type: Optional[str] = Query(None, alias="type"),
    revoked: Optional[bool] = Query(None),
    source: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """List stored STIX 2.1 objects strictly scoped to the requesting tenant."""
    stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)
    if object_type:
        stmt = stmt.where(StixObject.type == object_type.lower())
    if revoked is not None:
        stmt = stmt.where(StixObject.revoked == revoked)
    if source:
        stmt = stmt.where(StixObject.source == source)
    stmt = stmt.order_by(StixObject.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/objects/{stix_id}", response_model=StixObjectResponse)
async def get_stix_object(
    stix_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve a single STIX 2.1 object strictly scoped to the requesting tenant."""
    stmt = select(StixObject).where(
        StixObject.stix_id == stix_id,
        StixObject.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()

    if not obj:
        # Check tenant disambiguated ID
        disambiguated = f"{stix_id}-{tenant_id[:8]}"
        stmt_dis = select(StixObject).where(
            StixObject.stix_id == disambiguated,
            StixObject.tenant_id == tenant_id,
        )
        obj = (await db.execute(stmt_dis)).scalar_one_or_none()

    if not obj:
        raise HTTPException(status_code=404, detail="STIX 2.1 object not found")
    return obj

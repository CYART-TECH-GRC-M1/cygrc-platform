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

router = APIRouter()


class StixObjectCreate(BaseModel):
    stix_id: Optional[str] = None
    type: str  # indicator, malware, threat-actor, vulnerability
    spec_version: str = "2.1"
    name: Optional[str] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
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
    object_id = payload.stix_id or f"{payload.type.lower()}--{uuid.uuid4()}"

    stix_obj = StixObject(
        stix_id=object_id,
        tenant_id=tenant_id,
        type=payload.type.lower(),
        spec_version=payload.spec_version,
        name=payload.name,
        description=payload.description,
        pattern=payload.pattern,
        labels=payload.labels or [],
        confidence=payload.confidence,
        raw_stix=payload.raw_stix or {},
    )
    db.add(stix_obj)
    await db.commit()
    await db.refresh(stix_obj)
    return stix_obj


@router.get("/objects", response_model=List[StixObjectResponse])
async def list_stix_objects(
    object_type: Optional[str] = Query(None, alias="type"),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StixObject).where(StixObject.tenant_id == tenant_id)
    if object_type:
        stmt = stmt.where(StixObject.type == object_type.lower())
    stmt = stmt.order_by(StixObject.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/objects/{stix_id}", response_model=StixObjectResponse)
async def get_stix_object(
    stix_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(StixObject).where(
        StixObject.stix_id == stix_id,
        StixObject.tenant_id == tenant_id
    )
    result = await db.execute(stmt)
    obj = result.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="STIX 2.1 object not found")
    return obj

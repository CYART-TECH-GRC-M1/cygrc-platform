from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.asset import Asset
from backend.services.asset_discovery import AssetDiscoveryService
from backend.services.scan_scheduler import ScanSchedulerService

router = APIRouter()


class AssetCreate(BaseModel):
    name: str
    asset_type: str = "SERVER"  # SERVER, WORKSTATION, CLOUD, NETWORK, CONTAINER, WEB_APP
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    status: str = "ACTIVE"
    tags: Optional[List[str]] = []


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None


class ScanScheduleRequest(BaseModel):
    asset_id: str
    asset_name: str
    scan_type: Optional[str] = "FULL_VAPT"
    frequency: Optional[str] = "DAILY"


class AssetResponse(BaseModel):
    asset_id: str
    tenant_id: Optional[str] = None
    name: str
    asset_type: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: str
    status: str
    tags: Optional[List[str]] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    payload: AssetCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    asset = Asset(
        tenant_id=tenant_id,
        name=payload.name,
        asset_type=payload.asset_type.upper(),
        ip_address=payload.ip_address,
        hostname=payload.hostname,
        criticality=payload.criticality.upper(),
        status=payload.status.upper(),
        tags=payload.tags or [],
    )
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.post("/scan-schedules", status_code=status.HTTP_201_CREATED)
async def create_asset_scan_schedule(
    payload: ScanScheduleRequest,
    tenant_id: str = Depends(get_current_tenant_id),
):
    """Schedule automated network & web application vulnerability scan for an asset."""
    result = ScanSchedulerService.create_scan_schedule(
        asset_id=payload.asset_id,
        asset_name=payload.asset_name,
        scan_type=payload.scan_type or "FULL_VAPT",
        frequency=payload.frequency or "DAILY",
        tenant_id=tenant_id
    )
    return result


@router.post("/discover/nmap", response_model=List[AssetResponse])
async def discover_nmap_assets(
    payload: Dict[str, Any],
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    assets = await AssetDiscoveryService.process_nmap_discovery(
        scan_payload=payload,
        tenant_id=tenant_id,
        db=db
    )
    return assets


@router.post("/discover/cloud", response_model=List[AssetResponse])
async def discover_cloud_assets(
    payload: Dict[str, Any],
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    assets = await AssetDiscoveryService.process_cloud_inventory(
        inventory_payload=payload,
        tenant_id=tenant_id,
        db=db
    )
    return assets


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = Query(None),
    criticality: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.tenant_id == tenant_id)
    if asset_type:
        stmt = stmt.where(Asset.asset_type == asset_type.upper())
    if criticality:
        stmt = stmt.where(Asset.criticality == criticality.upper())
    stmt = stmt.order_by(Asset.created_at.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.asset_id == asset_id, Asset.tenant_id == tenant_id)
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    payload: AssetUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.asset_id == asset_id, Asset.tenant_id == tenant_id)
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    if payload.name is not None:
        asset.name = payload.name
    if payload.asset_type is not None:
        asset.asset_type = payload.asset_type.upper()
    if payload.ip_address is not None:
        asset.ip_address = payload.ip_address
    if payload.hostname is not None:
        asset.hostname = payload.hostname
    if payload.criticality is not None:
        asset.criticality = payload.criticality.upper()
    if payload.status is not None:
        asset.status = payload.status.upper()
    if payload.tags is not None:
        asset.tags = payload.tags

    asset.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.asset_id == asset_id, Asset.tenant_id == tenant_id)
    result = await db.execute(stmt)
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    await db.delete(asset)
    await db.commit()
    return None

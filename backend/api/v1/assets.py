from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.asset import Asset
from backend.models.scan_schedule import ScanSchedule, ScanJob
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
    environment: Optional[str] = "PROD"  # PROD, STAGING, DEV, TEST
    exposure: Optional[str] = "INTERNAL"  # INTERNAL, EXTERNAL, DMZ, CLOUD
    owner: Optional[str] = None
    os_name: Optional[str] = None
    tags: Optional[List[str]] = []


class AssetUpdate(BaseModel):
    name: Optional[str] = None
    asset_type: Optional[str] = None
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: Optional[str] = None
    status: Optional[str] = None
    environment: Optional[str] = None
    exposure: Optional[str] = None
    owner: Optional[str] = None
    os_name: Optional[str] = None
    tags: Optional[List[str]] = None


class AssetRetireRequest(BaseModel):
    reason: Optional[str] = "Asset retired by administrator"


class ScanScheduleRequest(BaseModel):
    asset_id: Optional[str] = None
    asset_name: Optional[str] = None
    target: Optional[str] = None
    scan_type: Optional[str] = "FULL_VAPT"
    frequency: Optional[str] = "DAILY"
    concurrency_limit: Optional[int] = 2


class UpdateScheduleStatusRequest(BaseModel):
    status: str  # ACTIVE, PAUSED, CANCELLED, COMPLETED


class TriggerScanJobRequest(BaseModel):
    target: str
    scan_type: Optional[str] = "NETWORK_NMAP"
    schedule_id: Optional[str] = None
    asset_id: Optional[str] = None


class CloudDiscoveryRequest(BaseModel):
    provider: str  # AWS, AZURE, GCP


class AssetResponse(BaseModel):
    asset_id: str
    tenant_id: Optional[str] = None
    name: str
    asset_type: str
    ip_address: Optional[str] = None
    hostname: Optional[str] = None
    criticality: str
    status: str
    environment: Optional[str] = "PROD"
    exposure: Optional[str] = "INTERNAL"
    owner: Optional[str] = None
    os_name: Optional[str] = None
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
        environment=(payload.environment or "PROD").upper(),
        exposure=(payload.exposure or "INTERNAL").upper(),
        owner=payload.owner,
        os_name=payload.os_name,
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
    db: AsyncSession = Depends(get_db),
):
    """Schedule automated network & web application vulnerability scan for an asset."""
    target_val = payload.target or payload.asset_name or payload.asset_id or "127.0.0.1"
    result = await ScanSchedulerService.create_scan_schedule(
        tenant_id=tenant_id,
        target=target_val,
        asset_id=payload.asset_id,
        asset_name=payload.asset_name,
        scan_type=payload.scan_type or "FULL_VAPT",
        frequency=payload.frequency or "DAILY",
        concurrency_limit=payload.concurrency_limit or 2,
        db=db,
    )
    return result


@router.get("/scan-schedules")
async def list_scan_schedules(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Lists all active and paused scan schedules for current tenant."""
    stmt = select(ScanSchedule).where(ScanSchedule.tenant_id == tenant_id).order_by(ScanSchedule.created_at.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.patch("/scan-schedules/{schedule_id}/status")
async def update_scan_schedule_status(
    schedule_id: str,
    payload: UpdateScheduleStatusRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Pauses, resumes, or cancels an existing scan schedule."""
    try:
        return await ScanSchedulerService.update_schedule_status(
            schedule_id=schedule_id,
            tenant_id=tenant_id,
            new_status=payload.status,
            db=db,
        )
    except LookupError:
        raise HTTPException(status_code=404, detail="Scan schedule not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/scan-jobs", status_code=status.HTTP_201_CREATED)
async def trigger_scan_job(
    payload: TriggerScanJobRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Triggers an authorized scan job, validating scope, concurrency, and deduplication."""
    res = await ScanSchedulerService.trigger_scan_job(
        tenant_id=tenant_id,
        target=payload.target,
        scan_type=payload.scan_type or "NETWORK_NMAP",
        schedule_id=payload.schedule_id,
        asset_id=payload.asset_id,
        db=db,
    )
    if not res.get("success") and res.get("status") in ("SCOPE_REJECTED", "CONCURRENCY_LIMIT_EXCEEDED", "CONCURRENT_JOB_RUNNING"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res


@router.get("/scan-jobs")
async def list_scan_jobs(
    schedule_id: Optional[str] = None,
    limit: int = 50,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves execution history of scan jobs for this tenant."""
    return await ScanSchedulerService.list_jobs(
        tenant_id=tenant_id,
        db=db,
        schedule_id=schedule_id,
        limit=limit,
    )


@router.get("/scan-jobs/{job_id}")
async def get_scan_job(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves full details and raw output of a specific scan job."""
    stmt = select(ScanJob).where(ScanJob.job_id == job_id, ScanJob.tenant_id == tenant_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Scan job not found")
    return job


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


@router.post("/discover/cloud-live")
async def trigger_live_cloud_discovery(
    payload: CloudDiscoveryRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Triggers live authenticated cloud discovery for AWS, Azure, or GCP."""
    res = await AssetDiscoveryService.run_live_cloud_discovery(
        provider=payload.provider,
        tenant_id=tenant_id,
        db=db,
    )
    if not res.get("success") and res.get("status") in ("UNSUPPORTED_PROVIDER", "PROVIDER_UNCONFIGURED"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=res)
    return res


@router.get("", response_model=List[AssetResponse])
async def list_assets(
    asset_type: Optional[str] = Query(None),
    criticality: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Asset).where(Asset.tenant_id == tenant_id)
    if asset_type:
        stmt = stmt.where(Asset.asset_type == asset_type.upper())
    if criticality:
        stmt = stmt.where(Asset.criticality == criticality.upper())
    if status:
        stmt = stmt.where(Asset.status == status.upper())
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


@router.post("/{asset_id}/retire", response_model=AssetResponse)
async def retire_asset(
    asset_id: str,
    payload: Optional[AssetRetireRequest] = None,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Authorized retirement/decommissioning of an asset."""
    reason = payload.reason if payload else "Asset retired by administrator"
    try:
        asset = await AssetDiscoveryService.retire_asset(
            asset_id=asset_id,
            tenant_id=tenant_id,
            reason=reason,
            db=db,
        )
        return asset
    except LookupError:
        raise HTTPException(status_code=404, detail="Asset not found")


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
    if payload.environment is not None:
        asset.environment = payload.environment.upper()
    if payload.exposure is not None:
        asset.exposure = payload.exposure.upper()
    if payload.owner is not None:
        asset.owner = payload.owner
    if payload.os_name is not None:
        asset.os_name = payload.os_name
    if payload.tags is not None:
        asset.tags = payload.tags

    asset.updated_at = datetime.now(timezone.utc)
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

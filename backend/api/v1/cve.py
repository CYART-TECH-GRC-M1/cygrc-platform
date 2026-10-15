from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.cve_finding import CVEFinding
from backend.services.cve_feed_service import CVEFeedService
from backend.services.vulnerability_prioritization import VulnerabilityPrioritizationService
from backend.services.grc_evidence_bridge import GRCEvidenceBridgeService
from backend.api.v1.findings import router as findings_router

router = APIRouter()
router.include_router(findings_router, prefix="/findings", tags=["VAPT Scanner - Findings"])


class CVEResponse(BaseModel):
    cve_id: str
    cvss_score: Optional[float] = None
    cvss_vector: Optional[str] = None
    cisa_kev: bool
    summary: Optional[str] = None
    remediation: Optional[str] = None
    affected_product: Optional[str] = None
    published_date: datetime

    class Config:
        from_attributes = True


class CVESyncRequest(BaseModel):
    feed_source: Optional[str] = "NVD_CISA_KEV"
    entries: Optional[List[Dict[str, Any]]] = None
    use_live_feed: Optional[bool] = False


class PrioritizeCalculateRequest(BaseModel):
    cvss_score: Optional[float] = None
    is_cisa_kev: bool = False
    asset_criticality: str = "HIGH"  # LOW, MEDIUM, HIGH, CRITICAL
    has_mitigating_control: bool = False


class GRCEvidenceFeedRequest(BaseModel):
    cve_id: str
    cvss_score: float
    affected_product: str
    control_code: Optional[str] = "A.12.6.1"


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_cve_feeds(
    payload: CVESyncRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await CVEFeedService.sync_daily_cve_feeds(
        cve_entries=payload.entries,
        use_live_feed=payload.use_live_feed or False,
        db=db
    )
    return result


@router.get("/feed-status")
async def get_cve_feed_status():
    """Returns feed freshness metadata, last sync timestamp, and active CISA KEV count."""
    return CVEFeedService.get_feed_status()


@router.post("/prioritize")
async def calculate_vulnerability_priority(payload: PrioritizeCalculateRequest):
    result = VulnerabilityPrioritizationService.calculate_priority_score(
        cvss_score=payload.cvss_score,
        is_cisa_kev=payload.is_cisa_kev,
        asset_criticality=payload.asset_criticality,
        has_mitigating_control=payload.has_mitigating_control
    )
    return result


@router.post("/evidence/feed-to-grc")
async def feed_vapt_evidence_to_grc(
    payload: GRCEvidenceFeedRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Feed VAPT scan results directly to Module 1 GRC Compliance Engine as automated evidence."""
    result = await GRCEvidenceBridgeService.feed_vapt_to_grc(
        cve_id=payload.cve_id,
        cvss_score=payload.cvss_score,
        affected_product=payload.affected_product,
        tenant_id=tenant_id,
        control_code=payload.control_code or "A.12.6.1",
        db=db,
    )
    return result


@router.get("", response_model=List[CVEResponse])
async def list_cves(
    cisa_kev_only: Optional[bool] = Query(False, alias="cisa_kev"),
    min_cvss: Optional[float] = Query(None, alias="min_cvss"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CVEFinding)
    if cisa_kev_only:
        stmt = stmt.where(CVEFinding.cisa_kev.is_(True))
    if min_cvss is not None:
        stmt = stmt.where(CVEFinding.cvss_score >= min_cvss)
    stmt = stmt.order_by(CVEFinding.cvss_score.desc())

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{cve_id}", response_model=CVEResponse)
async def get_cve_details(
    cve_id: str,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CVEFinding).where(CVEFinding.cve_id == cve_id)
    result = await db.execute(stmt)
    cve = result.scalar_one_or_none()
    if not cve:
        raise HTTPException(status_code=404, detail="CVE record not found")
    return cve

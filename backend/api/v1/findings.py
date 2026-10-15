"""Vulnerability Findings Management API Router.

Features:
- Lifecycle tracking connecting Asset -> Scan Job -> Finding -> CVE Enrichment -> Jira Remediation.
- Strict tenant isolation and authorized asset verification.
- Integrated priority score calculation with explainable breakdowns.
- Scanner connectivity health status checks for Nmap, ZAP, and OpenVAS.
- Idempotent Jira ticket synchronization.
"""
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.audit import record_audit_log
from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.asset import Asset
from backend.models.cve_finding import CVEFinding
from backend.models.vulnerability_finding import VulnerabilityFinding
from backend.services.jira_service import JiraIntegrationService
from backend.services.scanner_adapters import (
    NmapScannerAdapter,
    OWASPZapAdapter,
    OpenVASScannerAdapter,
)
from backend.services.vulnerability_prioritization import VulnerabilityPrioritizationService

router = APIRouter()


class FindingCreate(BaseModel):
    asset_id: str
    title: str
    severity: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    cve_id: Optional[str] = None
    cvss_score: Optional[float] = None
    scanner_source: str = "MANUAL"  # NMAP, ZAP, OPENVAS, MANUAL
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    scan_job_id: Optional[str] = None
    has_mitigating_control: bool = False


class FindingUpdate(BaseModel):
    status: Optional[str] = None  # OPEN, IN_REVIEW, REMEDIATING, REMEDIATED, FALSE_POSITIVE, ACCEPTED_RISK
    severity: Optional[str] = None
    remediation_notes: Optional[str] = None
    remediation: Optional[str] = None


class FindingResponse(BaseModel):
    finding_id: str
    tenant_id: str
    asset_id: str
    scan_job_id: Optional[str] = None
    cve_id: Optional[str] = None
    title: str
    severity: str
    cvss_score: Optional[float] = None
    cisa_kev: bool = False
    priority_score: float
    priority_level: str
    scanner_source: str
    evidence: Optional[str] = None
    remediation: Optional[str] = None
    status: str
    remediation_notes: Optional[str] = None
    jira_ticket_key: Optional[str] = None
    jira_ticket_url: Optional[str] = None
    first_observed_at: datetime
    last_observed_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/scanners/health")
async def get_scanners_health():
    """Returns connectivity and availability status of Nmap, OWASP ZAP, and OpenVAS."""
    nmap_status = NmapScannerAdapter.check_availability()
    zap_status = await OWASPZapAdapter.check_connection()
    openvas_status = OpenVASScannerAdapter.check_connection()

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "scanners": {
            "nmap": nmap_status,
            "owasp_zap": zap_status,
            "openvas": openvas_status,
        },
    }


@router.post("", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_vulnerability_finding(
    payload: FindingCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Creates a new vulnerability finding linked to an existing tenant asset."""
    # 1. Verify target asset exists and belongs to tenant
    asset_stmt = select(Asset).where(Asset.asset_id == payload.asset_id, Asset.tenant_id == tenant_id)
    asset_res = await db.execute(asset_stmt)
    asset = asset_res.scalar_one_or_none()
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Affected asset '{payload.asset_id}' not found for this tenant.",
        )

    now = datetime.now(timezone.utc)
    is_cisa_kev = False
    effective_cvss = payload.cvss_score
    remediation = payload.remediation

    # 2. Enrich with CVE feed data if CVE ID provided
    if payload.cve_id:
        cve_stmt = select(CVEFinding).where(CVEFinding.cve_id == payload.cve_id)
        cve_res = await db.execute(cve_stmt)
        cve_record = cve_res.scalar_one_or_none()
        if cve_record:
            is_cisa_kev = cve_record.cisa_kev
            if effective_cvss is None:
                effective_cvss = cve_record.cvss_score
            if not remediation:
                remediation = cve_record.remediation

    # 3. Calculate Prioritized Score
    priority_calc = VulnerabilityPrioritizationService.calculate_priority_score(
        cvss_score=effective_cvss,
        is_cisa_kev=is_cisa_kev,
        asset_criticality=asset.criticality,
        has_mitigating_control=payload.has_mitigating_control,
    )

    finding = VulnerabilityFinding(
        tenant_id=tenant_id,
        asset_id=payload.asset_id,
        scan_job_id=payload.scan_job_id,
        cve_id=payload.cve_id,
        title=payload.title,
        severity=payload.severity.upper(),
        cvss_score=effective_cvss,
        cisa_kev=is_cisa_kev,
        priority_score=priority_calc["priority_score"],
        priority_level=priority_calc["priority_level"],
        scanner_source=payload.scanner_source.upper(),
        evidence=payload.evidence,
        remediation=remediation,
        status="OPEN",
        first_observed_at=now,
        last_observed_at=now,
    )

    db.add(finding)
    await db.commit()
    await db.refresh(finding)

    await record_audit_log(
        action="vulnerability_finding:create",
        tenant_id=tenant_id,
        resource_type="vulnerability_finding",
        resource_id=finding.finding_id,
        details={
            "asset_id": finding.asset_id,
            "cve_id": finding.cve_id,
            "priority_score": finding.priority_score,
            "priority_level": finding.priority_level,
        },
        db=db,
    )

    return finding


@router.get("", response_model=List[FindingResponse])
async def list_vulnerability_findings(
    asset_id: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    scanner_source: Optional[str] = Query(None),
    min_priority: Optional[float] = Query(None),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Lists vulnerability findings for tenant with filtering and sorting by priority."""
    stmt = select(VulnerabilityFinding).where(VulnerabilityFinding.tenant_id == tenant_id)

    if asset_id:
        stmt = stmt.where(VulnerabilityFinding.asset_id == asset_id)
    if severity:
        stmt = stmt.where(VulnerabilityFinding.severity == severity.upper())
    if status_filter:
        stmt = stmt.where(VulnerabilityFinding.status == status_filter.upper())
    if scanner_source:
        stmt = stmt.where(VulnerabilityFinding.scanner_source == scanner_source.upper())
    if min_priority is not None:
        stmt = stmt.where(VulnerabilityFinding.priority_score >= min_priority)

    stmt = stmt.order_by(VulnerabilityFinding.priority_score.desc())
    res = await db.execute(stmt)
    return res.scalars().all()


@router.get("/{finding_id}", response_model=FindingResponse)
async def get_vulnerability_finding(
    finding_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieves single finding by finding_id."""
    stmt = select(VulnerabilityFinding).where(
        VulnerabilityFinding.finding_id == finding_id,
        VulnerabilityFinding.tenant_id == tenant_id,
    )
    res = await db.execute(stmt)
    finding = res.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Vulnerability finding not found")
    return finding


@router.patch("/{finding_id}", response_model=FindingResponse)
async def update_vulnerability_finding(
    finding_id: str,
    payload: FindingUpdate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Updates remediation status or notes on a finding."""
    stmt = select(VulnerabilityFinding).where(
        VulnerabilityFinding.finding_id == finding_id,
        VulnerabilityFinding.tenant_id == tenant_id,
    )
    res = await db.execute(stmt)
    finding = res.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Vulnerability finding not found")

    if payload.status:
        finding.status = payload.status.upper()
    if payload.severity:
        finding.severity = payload.severity.upper()
    if payload.remediation_notes is not None:
        finding.remediation_notes = payload.remediation_notes
    if payload.remediation is not None:
        finding.remediation = payload.remediation

    finding.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(finding)
    return finding


@router.post("/{finding_id}/push-jira")
async def push_finding_to_jira(
    finding_id: str,
    project_key: Optional[str] = "CYGRC",
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Pushes a finding to Jira with idempotency check to prevent duplicate tickets."""
    stmt = select(VulnerabilityFinding).where(
        VulnerabilityFinding.finding_id == finding_id,
        VulnerabilityFinding.tenant_id == tenant_id,
    )
    res = await db.execute(stmt)
    finding = res.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Vulnerability finding not found")

    result = await JiraIntegrationService.push_remediation_ticket_async(
        cve_id=finding.cve_id or finding.title,
        cvss_score=finding.cvss_score,
        affected_product=f"Asset {finding.asset_id}",
        summary=finding.title,
        project_key=project_key or "CYGRC",
        finding_id=finding.finding_id,
        asset_id=finding.asset_id,
        existing_ticket_key=finding.jira_ticket_key,
        existing_ticket_url=finding.jira_ticket_url,
        db=db,
    )

    return result

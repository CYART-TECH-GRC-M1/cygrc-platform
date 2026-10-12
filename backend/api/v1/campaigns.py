from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.campaign import (
    RedTeamCampaign,
    RedTeamExecutionJob,
    AtomicTestExecution,
    CampaignReport,
)
from backend.services.mitre_attack import MitreAttackService
from backend.services.atomic_runner import AtomicRunnerService
from backend.services.campaign_reporting import CampaignReportingService

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    authorized_scope: Optional[Dict[str, Any]] = Field(default_factory=dict)
    approved_targets: Optional[List[str]] = Field(default_factory=list)
    status: str = "ACTIVE"
    approval_status: str = "APPROVED"
    operator_id: Optional[str] = "lead-operator"
    schedule_type: str = "MANUAL"
    scheduled_at: Optional[datetime] = None
    techniques_tested: Optional[List[str]] = ["T1059.001", "T1003.001", "T1053.005"]
    technique_catalogue: Optional[List[Any]] = Field(default_factory=list)


class CampaignApprovalRequest(BaseModel):
    approval_status: str  # APPROVED or REJECTED
    approved_by: str = "security-director"


class CampaignExecuteRequest(BaseModel):
    target_asset_ids: Optional[List[str]] = None
    technique_ids: Optional[List[str]] = None
    operator_id: Optional[str] = "red-team-operator"


class CampaignResponse(BaseModel):
    campaign_id: str
    tenant_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    objective: Optional[str] = None
    authorized_scope: Optional[Dict[str, Any]] = None
    approved_targets: Optional[List[str]] = []
    status: str
    approval_status: Optional[str] = "APPROVED"
    approved_by: Optional[str] = None
    operator_id: Optional[str] = None
    schedule_type: Optional[str] = "MANUAL"
    techniques_tested: Optional[List[str]] = []
    coverage_score: Optional[str] = "0%"
    execution_summary: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a persistent Red Team campaign with authorized scope, target inventory,
    technique catalogue, and approval status.
    Calculates dynamic coverage without hardcoding a 222 denominator.
    """
    techniques = payload.techniques_tested or []
    catalog_len = len(MitreAttackService.get_all_techniques())
    coverage_pct = f"{round((len(techniques) / catalog_len) * 100, 1)}%" if catalog_len > 0 else "0.0%"

    campaign = RedTeamCampaign(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        objective=payload.objective or payload.description,
        authorized_scope=payload.authorized_scope or {},
        approved_targets=payload.approved_targets or [],
        status=payload.status.upper(),
        approval_status=payload.approval_status.upper(),
        operator_id=payload.operator_id,
        schedule_type=payload.schedule_type.upper(),
        scheduled_at=payload.scheduled_at,
        techniques_tested=techniques,
        technique_catalogue=payload.technique_catalogue or [],
        coverage_score=coverage_pct,
        execution_summary={
            "total_planned": len(techniques),
            "total_executed": 0,
            "total_detected": 0,
            "detection_gaps": 0,
        },
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RedTeamCampaign)
        .where(RedTeamCampaign.tenant_id == tenant_id)
        .order_by(RedTeamCampaign.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RedTeamCampaign).where(
        RedTeamCampaign.campaign_id == campaign_id,
        RedTeamCampaign.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.patch("/{campaign_id}/approval", response_model=CampaignResponse)
async def update_campaign_approval(
    campaign_id: str,
    payload: CampaignApprovalRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Updates campaign approval status. Unapproved campaigns cannot be executed.
    """
    stmt = select(RedTeamCampaign).where(
        RedTeamCampaign.campaign_id == campaign_id,
        RedTeamCampaign.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    new_status = payload.approval_status.upper()
    if new_status not in ["APPROVED", "REJECTED", "PENDING_APPROVAL"]:
        raise HTTPException(status_code=400, detail="Invalid approval status")

    campaign.approval_status = new_status
    campaign.approved_by = payload.approved_by
    campaign.approved_at = datetime.utcnow()
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: str,
    payload: Optional[CampaignExecuteRequest] = None,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Executes planned techniques in campaign.
    Validates target authorization before every execution.
    """
    stmt = select(RedTeamCampaign).where(
        RedTeamCampaign.campaign_id == campaign_id,
        RedTeamCampaign.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.approval_status != "APPROVED":
        raise HTTPException(
            status_code=400,
            detail=f"Campaign is in '{campaign.approval_status}' state. Execution requires APPROVED status.",
        )

    targets = (payload.target_asset_ids if payload and payload.target_asset_ids else None) or campaign.approved_targets or []
    if not targets:
        raise HTTPException(status_code=400, detail="No approved targets specified for campaign execution")

    techniques = (payload.technique_ids if payload and payload.technique_ids else None) or campaign.techniques_tested or []
    if not techniques:
        raise HTTPException(status_code=400, detail="No planned techniques specified for campaign execution")

    campaign.status = "RUNNING"
    await db.commit()

    executed_jobs = []
    errors = []

    for target_id in targets:
        for tech_id in techniques:
            try:
                # Validates target authorization and runs safe sandboxed test
                exec_record = await AtomicRunnerService.execute_test(
                    db=db,
                    tenant_id=tenant_id,
                    technique_id=tech_id,
                    technique_name=f"Technique {tech_id}",
                    target_asset_id=target_id,
                    campaign_id=campaign_id,
                    operator_id=payload.operator_id if payload else campaign.operator_id,
                )
                executed_jobs.append({
                    "execution_id": exec_record.execution_id,
                    "technique_id": exec_record.technique_id,
                    "target_asset_id": exec_record.target_asset_id,
                    "status": exec_record.status,
                    "exit_code": exec_record.exit_code,
                })
            except Exception as e:
                errors.append({
                    "target_asset_id": target_id,
                    "technique_id": tech_id,
                    "error": str(e),
                })

    campaign.status = "ACTIVE" if not errors else "PARTIAL_FAILURE"
    await db.commit()

    return {
        "campaign_id": campaign_id,
        "status": campaign.status,
        "executed_count": len(executed_jobs),
        "failed_count": len(errors),
        "executions": executed_jobs,
        "errors": errors,
    }


@router.post("/{campaign_id}/cancel")
async def cancel_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Cancels an active or scheduled campaign.
    """
    stmt = select(RedTeamCampaign).where(
        RedTeamCampaign.campaign_id == campaign_id,
        RedTeamCampaign.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = "CANCELLED"
    await db.commit()
    return {"campaign_id": campaign_id, "status": "CANCELLED", "timestamp": datetime.utcnow()}


@router.get("/{campaign_id}/jobs")
async def list_campaign_jobs(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(RedTeamExecutionJob)
        .where(
            RedTeamExecutionJob.campaign_id == campaign_id,
            RedTeamExecutionJob.tenant_id == tenant_id,
        )
        .order_by(RedTeamExecutionJob.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{campaign_id}/heatmap")
async def get_campaign_attack_heatmap(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Generates MITRE ATT&CK coverage heat map matrix for specified Red Team Campaign."""
    stmt = select(RedTeamCampaign).where(
        RedTeamCampaign.campaign_id == campaign_id,
        RedTeamCampaign.tenant_id == tenant_id,
    )
    result = await db.execute(stmt)
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    tested_set = set(t.lower() for t in (campaign.techniques_tested or []))
    matrix = MitreAttackService.get_full_matrix()

    heatmap_tactics = []
    covered_count = 0

    for tactic in matrix["matrix"]:
        tactic_techs = []
        for tech in tactic["techniques"]:
            is_tested = tech["id"].lower() in tested_set
            if is_tested:
                covered_count += 1
            tactic_techs.append({
                "technique_id": tech["id"],
                "name": tech["name"],
                "tested": is_tested,
                "status": "PASS" if is_tested else "UNTESTED",
            })

        heatmap_tactics.append({
            "tactic_id": tactic["tactic_id"],
            "tactic_name": tactic["tactic_name"],
            "techniques": tactic_techs,
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "techniques_tested_count": len(campaign.techniques_tested or []),
        "coverage_percentage": campaign.coverage_score,
        "heatmap": heatmap_tactics,
    }


@router.post("/{campaign_id}/generate-report")
async def generate_campaign_report(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Generates and persists final post-campaign assessment report linking findings
    to SOC detection engineering backlog.
    """
    try:
        report = await CampaignReportingService.generate_final_report(
            db=db,
            tenant_id=tenant_id,
            campaign_id=campaign_id,
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{campaign_id}/report")
async def get_campaign_report(
    campaign_id: str,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    report = await CampaignReportingService.get_latest_report(
        db=db,
        tenant_id=tenant_id,
        campaign_id=campaign_id,
    )
    if not report:
        raise HTTPException(status_code=404, detail="Campaign report not yet generated")
    return report

from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.core.database import get_db
from backend.core.dependencies import get_current_tenant_id
from backend.models.campaign import RedTeamCampaign
from backend.services.mitre_attack import MitreAttackService

router = APIRouter()


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "ACTIVE"
    techniques_tested: Optional[List[str]] = ["T1059.001", "T1003.001", "T1053.005"]


class CampaignResponse(BaseModel):
    campaign_id: str
    tenant_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: str
    techniques_tested: Optional[List[str]] = []
    coverage_score: Optional[str] = "0%"
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
    techniques = payload.techniques_tested or []
    total_mitre_techniques = 222
    coverage_pct = f"{round((len(techniques) / total_mitre_techniques) * 100, 1)}%"

    campaign = RedTeamCampaign(
        tenant_id=tenant_id,
        name=payload.name,
        description=payload.description,
        status=payload.status.upper(),
        techniques_tested=techniques,
        coverage_score=coverage_pct,
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
    stmt = select(RedTeamCampaign).where(RedTeamCampaign.tenant_id == tenant_id).order_by(RedTeamCampaign.created_at.desc())
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
        RedTeamCampaign.tenant_id == tenant_id
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
                "status": "PASS" if is_tested else "UNTESTED"
            })

        heatmap_tactics.append({
            "tactic_id": tactic["tactic_id"],
            "tactic_name": tactic["tactic_name"],
            "techniques": tactic_techs
        })

    return {
        "campaign_id": campaign_id,
        "campaign_name": campaign.name,
        "techniques_tested_count": len(campaign.techniques_tested or []),
        "coverage_percentage": campaign.coverage_score,
        "heatmap": heatmap_tactics
    }

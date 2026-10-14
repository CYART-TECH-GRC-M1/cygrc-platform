from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.services.jira_service import JiraIntegrationService

router = APIRouter()


class JiraPushRequest(BaseModel):
    cve_id: str
    cvss_score: Optional[float] = 5.0
    affected_product: str
    summary: str
    project_key: Optional[str] = "CYGRC"
    issue_type: Optional[str] = "Vulnerability"
    finding_id: Optional[str] = None
    asset_id: Optional[str] = None
    existing_ticket_key: Optional[str] = None
    require_live: Optional[bool] = False


@router.post("/push", status_code=status.HTTP_201_CREATED)
async def push_cve_remediation_ticket(
    payload: JiraPushRequest,
    db: AsyncSession = Depends(get_db),
):
    """Pushes a high/critical CVE finding to Jira as an automated remediation ticket."""
    result = await JiraIntegrationService.push_remediation_ticket_async(
        cve_id=payload.cve_id,
        cvss_score=payload.cvss_score,
        affected_product=payload.affected_product,
        summary=payload.summary,
        project_key=payload.project_key or "CYGRC",
        issue_type=payload.issue_type or "Vulnerability",
        finding_id=payload.finding_id,
        asset_id=payload.asset_id,
        existing_ticket_key=payload.existing_ticket_key,
        require_live=payload.require_live or False,
        db=db,
    )
    if result.get("status") in ("AUTH_ERROR", "PERMISSION_DENIED", "RATE_LIMITED", "API_ERROR", "JIRA_UNCONFIGURED"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result,
        )
    return result


@router.get("/config")
def get_jira_configuration():
    """Returns Jira integration configuration and reachability status."""
    return JiraIntegrationService.check_configuration()

from typing import Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from backend.services.jira_service import JiraIntegrationService

router = APIRouter()


class JiraPushRequest(BaseModel):
    cve_id: str
    cvss_score: float
    affected_product: str
    summary: str
    project_key: Optional[str] = "CYGRC"
    issue_type: Optional[str] = "Vulnerability"


@router.post("/push", status_code=status.HTTP_201_CREATED)
async def push_cve_remediation_ticket(payload: JiraPushRequest):
    """Pushes a high/critical CVE finding to Jira as an automated remediation ticket."""
    result = JiraIntegrationService.push_remediation_ticket(
        cve_id=payload.cve_id,
        cvss_score=payload.cvss_score,
        affected_product=payload.affected_product,
        summary=payload.summary,
        project_key=payload.project_key or "CYGRC",
        issue_type=payload.issue_type or "Vulnerability"
    )
    return result

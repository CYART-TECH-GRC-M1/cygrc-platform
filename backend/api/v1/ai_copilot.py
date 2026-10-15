import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from backend.core.dependencies import get_current_tenant_id
from backend.core.ai_guardrails import CyberAIGuardrails
from backend.services.ai_threat_analyzer import AIThreatAnalyzerService

router = APIRouter()


class AICopilotDraftRequest(BaseModel):
    alert_id: Optional[str] = None
    case_id: Optional[str] = None
    context_text: Optional[str] = "Suspicious PowerShell command execution with encoded payload"
    draft_type: str = "triage_questions"  # triage_questions, case_notes, remediation_steps, executive_summary


class AIHumanApproveRequest(BaseModel):
    human_approval_token: str
    reviewer_email: str


class AICaseClosureSummaryRequest(BaseModel):
    case_id: str
    case_number: str = "INC-2026-0001"
    title: str = "Unexplained Outbound Traffic Spike"
    summary: Optional[str] = "High volume exfiltration attempt."
    alerts_count: Optional[int] = 2


class AICopilotDraftResponse(BaseModel):
    draft_id: str
    tenant_id: str
    draft_type: str
    suggested_triage_questions: List[str]
    suggested_case_notes: str
    suggested_remediation_steps: List[str]
    is_draft: bool = True
    draft_watermark: str = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"
    human_approval_token: str
    timestamp: datetime


@router.post("/draft", response_model=AICopilotDraftResponse, status_code=status.HTTP_200_OK)
async def generate_ai_soc_draft(
    payload: AICopilotDraftRequest,
    tenant_id: str = Depends(get_current_tenant_id),
):
    draft_id = f"AIDRAFT-{uuid.uuid4().hex[:8].upper()}"
    approval_token = f"APPROVAL-TOKEN-{uuid.uuid4().hex[:12].upper()}"

    ctx = payload.context_text or "Security Event Alert"

    triage_questions = [
        "Was process execution authorized by system user or service account?",
        f"Has external IP in alert '{ctx[:40]}' communicated with other internal subnets?",
        "Are there any secondary persistence mechanisms created in Windows Registry or Systemd?",
        "Does endpoint have active Endpoint Detection & Response (EDR) isolation capability?"
    ]

    case_notes = (
        f"[AI SOC Copilot Analysis]\n"
        f"Trigger Context: {ctx}\n"
        f"Initial Threat Assessment: High potential for malicious payload execution.\n"
        f"Recommended Action: Isolate target endpoint from network segment and collect memory dump via Velociraptor."
    )

    remediation_steps = [
        "Isolate target host from active domain controller subnet.",
        "Revoke compromised user credentials and terminate active OAuth sessions.",
        "Perform forensic RAM image capture for chain-of-custody logging.",
        "Submit suspicious file hash to STIX 2.1 Threat Intel Store."
    ]

    resp = AICopilotDraftResponse(
        draft_id=draft_id,
        tenant_id=tenant_id,
        draft_type=payload.draft_type,
        suggested_triage_questions=triage_questions,
        suggested_case_notes=case_notes,
        suggested_remediation_steps=remediation_steps,
        is_draft=True,
        draft_watermark="DRAFT_SUBJECT_TO_HUMAN_APPROVAL",
        human_approval_token=approval_token,
        timestamp=datetime.utcnow(),
    )

    CyberAIGuardrails.validate_ai_draft_output(resp.dict())
    return resp


@router.post("/approve", status_code=status.HTTP_200_OK)
async def approve_ai_copilot_draft(payload: AIHumanApproveRequest):
    result = CyberAIGuardrails.sign_off_human_review(
        human_approval_token=payload.human_approval_token,
        reviewer_email=payload.reviewer_email
    )
    return result


@router.post("/case-closure-summary", status_code=status.HTTP_200_OK)
async def generate_ai_case_closure_summary(payload: AICaseClosureSummaryRequest):
    """AI Threat Analyzer generates structured executive summaries and root cause reports upon incident case closure."""
    result = AIThreatAnalyzerService.generate_case_closure_summary(
        case_id=payload.case_id,
        case_number=payload.case_number,
        title=payload.title,
        summary=payload.summary or "Incident resolved.",
        alerts_count=payload.alerts_count or 2
    )
    return result

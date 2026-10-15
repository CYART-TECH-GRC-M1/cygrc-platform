from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.capabilities import (
    SOCCopilotService,
    ThreatAnalyzerService,
    IncidentSummarizerService,
    RootCauseAnalysisService,
    ThreatHuntingService,
    RemediationGeneratorService,
    AttackPathPredictionService,
    ApprovalWorkflowService,
)
from backend.ai.llm import llm_client
from backend.ai.schemas import (
    SOCCopilotRequest,
    SOCCopilotResponse,
    ThreatAnalyzerRequest,
    ThreatAnalyzerResponse,
    IncidentSummarizerRequest,
    IncidentSummarizerResponse,
    RootCauseAnalysisRequest,
    RootCauseAnalysisResponse,
    ThreatHuntingRequest,
    ThreatHuntingResponse,
    RemediationGeneratorRequest,
    RemediationGeneratorResponse,
    AttackPathPredictionRequest,
    AttackPathPredictionResponse,
    ApprovalDecisionRequest,
    ApprovalActionResponse,
    ApprovalExecuteRequest,
    AIApprovalItem,
)
from backend.core.config import settings
from backend.core.database import get_db
from backend.core.dependencies import (
    get_current_tenant_id,
    get_current_user,
    require_role,
)
from backend.api.v1.ai_copilot import (
    AICopilotDraftRequest,
    AICopilotDraftResponse,
    AIHumanApproveRequest,
    AICaseClosureSummaryRequest,
    generate_ai_soc_draft,
    approve_ai_copilot_draft,
    generate_ai_case_closure_summary,
)

router = APIRouter()


# -------------------------------------------------------------------------
# Provider Status & Configuration Check
# -------------------------------------------------------------------------

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_ai_status():
    """Reports configured AI provider status and availability."""
    is_avail = llm_client.is_available()
    return {
        "provider": settings.AI_PROVIDER or "None",
        "model": settings.AI_MODEL,
        "status": "AVAILABLE" if is_avail else "UNAVAILABLE",
        "is_available": is_avail,
        "guardrails_active": True,
        "environment": settings.ENVIRONMENT,
    }


@router.post(
    "/eval/run",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Lead", "Tenant Admin", "Admin", "Super Admin", "Read-only Auditor", "Auditor"]))],
)
async def run_ai_evaluation_benchmark(db: AsyncSession = Depends(get_db)):
    """Runs the fixed Phase 7 AI evaluation benchmark suite and returns metrics."""
    from backend.ai.eval.runner import AIEvaluationRunner
    return await AIEvaluationRunner.run_evaluation(db)


# -------------------------------------------------------------------------
# 1. SOC Copilot Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/soc-copilot",
    response_model=SOCCopilotResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Tier 1", "SOC Tier 2", "SOC Lead", "Detection Engineer", "Threat Intelligence Analyst", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def soc_copilot_endpoint(
    payload: SOCCopilotRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Answer analyst questions using authorized tenant alerts, cases, and intelligence records."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await SOCCopilotService.query(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 2. Threat Analyzer Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/threat-analyzer",
    response_model=ThreatAnalyzerResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["Threat Intelligence Analyst", "SOC Tier 2", "SOC Lead", "Detection Engineer", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def threat_analyzer_endpoint(
    payload: ThreatAnalyzerRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze alert indicators and relevant threat intelligence, citing sources and expressing uncertainty."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await ThreatAnalyzerService.analyze(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 3. Incident Summariser Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/incident-summarizer",
    response_model=IncidentSummarizerResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Lead", "SOC Tier 2", "DFIR Investigator", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def incident_summarizer_endpoint(
    payload: IncidentSummarizerRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Summarize persisted incident timelines and supporting evidence."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await IncidentSummarizerService.summarize(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 4. Root Cause Analysis Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/root-cause-analysis",
    response_model=RootCauseAnalysisResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Lead", "DFIR Investigator", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def root_cause_analysis_endpoint(
    payload: RootCauseAnalysisRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate evidence-linked hypotheses, distinguish verified facts from hypotheses, and identify missing evidence."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await RootCauseAnalysisService.analyze(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 5. Threat Hunting Assistant Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/threat-hunting",
    response_model=ThreatHuntingResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["Detection Engineer", "Threat Intelligence Analyst", "SOC Lead", "Red Team Engineer", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def threat_hunting_endpoint(
    payload: ThreatHuntingRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Recommend investigation queries and hunting hypotheses grounded in available telemetry."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await ThreatHuntingService.formulate_hunt(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 6. Remediation Generator Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/remediation-generator",
    response_model=RemediationGeneratorResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["VAPT Engineer", "SOC Lead", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def remediation_generator_endpoint(
    payload: RemediationGeneratorRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate finding-linked remediation recommendations. Commands and scripts remain drafts until reviewed and approved."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await RemediationGeneratorService.generate(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# 7. Attack Path Prediction Endpoint
# -------------------------------------------------------------------------

@router.post(
    "/attack-path-prediction",
    response_model=AttackPathPredictionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["Red Team Engineer", "VAPT Engineer", "SOC Lead", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def attack_path_prediction_endpoint(
    payload: AttackPathPredictionRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze actual asset relationships, exposures, findings, and privilege relationships."""
    roles = [current_user.get("role")] + current_user.get("roles", [])
    user_roles = [r for r in roles if r]
    return await AttackPathPredictionService.predict(
        db=db,
        tenant_id=tenant_id,
        user_roles=user_roles,
        request=payload,
        actor_email=current_user.get("email"),
    )


# -------------------------------------------------------------------------
# Human-in-the-Loop Approvals Endpoints
# -------------------------------------------------------------------------

@router.get("/approvals", response_model=List[AIApprovalItem], status_code=status.HTTP_200_OK)
async def list_ai_approvals(
    status_filter: Optional[str] = Query("ALL", alias="status"),
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Query pending and decided AI sensitive action approvals."""
    return await ApprovalWorkflowService.list_approvals(
        db=db, tenant_id=tenant_id, status_filter=status_filter
    )


@router.post(
    "/approvals/{approval_id}/decision",
    response_model=ApprovalActionResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Lead", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "Platform Operator"]))],
)
async def decide_ai_approval(
    approval_id: str,
    payload: ApprovalDecisionRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """Human review sign-off decision (APPROVED or REJECTED) for sensitive AI actions."""
    return await ApprovalWorkflowService.decide_approval(
        db=db,
        tenant_id=tenant_id,
        approval_id=approval_id,
        request=payload,
    )


@router.post(
    "/approvals/{approval_id}/execute",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_role(["SOC Lead", "Tenant Admin", "Tenant Administrator", "Admin", "Super Admin", "VAPT Engineer", "DFIR Investigator"]))],
)
async def execute_approved_action(
    approval_id: str,
    payload: ApprovalExecuteRequest,
    tenant_id: str = Depends(get_current_tenant_id),
    db: AsyncSession = Depends(get_db),
):
    """
    Execute an approved AI action.
    Strictly verifies status == 'APPROVED' on the backend prior to dispatch.
    """
    return await ApprovalWorkflowService.execute_approved_action(
        db=db,
        tenant_id=tenant_id,
        approval_id=approval_id,
        approval_token=payload.approval_token,
        operator_email=payload.operator_email,
    )


# -------------------------------------------------------------------------
# Backwards Compatibility Endpoints (Preserving Phase 2 / Day 5-7 tests)
# -------------------------------------------------------------------------

@router.post("/draft", response_model=AICopilotDraftResponse, status_code=status.HTTP_200_OK)
async def legacy_ai_soc_draft(
    payload: AICopilotDraftRequest,
    tenant_id: str = Depends(get_current_tenant_id),
):
    return await generate_ai_soc_draft(payload=payload, tenant_id=tenant_id)


@router.post("/approve", status_code=status.HTTP_200_OK)
async def legacy_approve_draft(payload: AIHumanApproveRequest):
    return await approve_ai_copilot_draft(payload=payload)


@router.post("/case-closure-summary", status_code=status.HTTP_200_OK)
async def legacy_case_closure_summary(payload: AICaseClosureSummaryRequest):
    return await generate_ai_case_closure_summary(payload=payload)

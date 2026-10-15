import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.ai.guardrails import (
    CyberAIFoundationGuardrails,
    PromptInjectionDetector,
    SensitiveActionGuardrail,
)
from backend.ai.llm import LLMMessage, llm_client
from backend.ai.prompts import (
    SOC_COPILOT_SYSTEM_PROMPT,
    THREAT_ANALYZER_SYSTEM_PROMPT,
    INCIDENT_SUMMARISER_SYSTEM_PROMPT,
    ROOT_CAUSE_ANALYSIS_SYSTEM_PROMPT,
    THREAT_HUNTING_SYSTEM_PROMPT,
    REMEDIATION_GENERATOR_SYSTEM_PROMPT,
    ATTACK_PATH_PREDICTION_SYSTEM_PROMPT,
)
from backend.ai.rag import AuthorizedRetriever, AuthorizedSourceRecord
from backend.ai.schemas import (
    SOCCopilotRequest,
    SOCCopilotResponse,
    ThreatAnalyzerRequest,
    ThreatAnalyzerResponse,
    IndicatorAnalysis,
    IncidentSummarizerRequest,
    IncidentSummarizerResponse,
    TimelineEvent,
    RootCauseAnalysisRequest,
    RootCauseAnalysisResponse,
    VerifiedFact,
    Hypothesis,
    MissingEvidenceItem,
    ThreatHuntingRequest,
    ThreatHuntingResponse,
    HuntingHypothesis,
    HuntingQuery,
    RemediationGeneratorRequest,
    RemediationGeneratorResponse,
    DraftCommand,
    DraftScript,
    AttackPathPredictionRequest,
    AttackPathPredictionResponse,
    AttackPathStep,
    SourceReference,
    ApprovalDecisionRequest,
    ApprovalActionResponse,
    AIApprovalItem,
)
from backend.core.audit import record_audit_log
from backend.models.ai_approval import AIActionApproval
from backend.models.incident_case import IncidentCase

logger = logging.getLogger("cygrc.ai.capabilities")


def _build_source_references(
    verified_ids: List[str], authorized_map: Dict[str, AuthorizedSourceRecord]
) -> List[SourceReference]:
    refs = []
    seen = set()
    for vid in verified_ids:
        if vid in seen:
            continue
        seen.add(vid)
        rec = authorized_map.get(vid)
        if rec:
            refs.append(
                SourceReference(
                    record_id=rec.record_id,
                    record_type=rec.record_type,
                    title=rec.title,
                    verified=True,
                )
            )
        else:
            refs.append(
                SourceReference(
                    record_id=vid,
                    record_type="RECORD",
                    title=vid,
                    verified=True,
                )
            )
    return refs


# -------------------------------------------------------------------------
# 1. SOC Copilot Service
# -------------------------------------------------------------------------

class SOCCopilotService:
    @staticmethod
    async def query(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: SOCCopilotRequest,
        actor_email: Optional[str] = None,
    ) -> SOCCopilotResponse:
        PromptInjectionDetector.validate_user_input(request.query)

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            query_text=request.query,
            specific_alert_ids=request.alert_ids,
            specific_case_ids=request.case_ids,
        )

        # Check for safe refusal scenario if requested alert/case IDs were not found in tenant records
        requested_ids = (request.alert_ids or []) + (request.case_ids or [])
        if requested_ids and not any(rid in auth_map for rid in requested_ids):
            refusal_msg = CyberAIFoundationGuardrails.generate_safe_refusal(
                request.query, tenant_id
            )
            return SOCCopilotResponse(
                answer=refusal_msg,
                cited_sources=[],
                suggested_followups=["Verify that the alert or case identifier exists in the current tenant."],
                confidence="LOW",
                grounding_score=0.0,
                is_draft=True,
                draft_watermark=CyberAIFoundationGuardrails.DRAFT_WATERMARK,
            )

        messages = [
            LLMMessage(role="system", content=SOC_COPILOT_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Authorized Records:\n{context_str}\n\n"
                    f"Analyst Query: {request.query}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"answer": raw_output, "cited_sources": [], "suggested_followups": []}

        sanitized_answer, verified_ids, unverified_ids, score = (
            CyberAIFoundationGuardrails.sanitize_output(
                data.get("answer", raw_output), set(auth_map.keys())
            )
        )

        sources = _build_source_references(verified_ids, auth_map)

        await record_audit_log(
            action="AI_SOC_COPILOT_QUERY",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="SOC_COPILOT",
            details={
                "grounding_score": score,
                "verified_sources_count": len(verified_ids),
                "unverified_citations_count": len(unverified_ids),
            },
            db=db,
        )

        return SOCCopilotResponse(
            answer=sanitized_answer,
            cited_sources=sources,
            suggested_followups=data.get("suggested_followups", []),
            confidence=data.get("confidence", "HIGH" if score > 0.7 else "MEDIUM"),
            grounding_score=score,
            is_draft=True,
            draft_watermark=CyberAIFoundationGuardrails.DRAFT_WATERMARK,
        )


# -------------------------------------------------------------------------
# 2. Threat Analyzer Service
# -------------------------------------------------------------------------

class ThreatAnalyzerService:
    @staticmethod
    async def analyze(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: ThreatAnalyzerRequest,
        actor_email: Optional[str] = None,
    ) -> ThreatAnalyzerResponse:
        combined_input = f"{request.alert_id or ''} {' '.join(request.indicators or [])} {request.context or ''}"
        PromptInjectionDetector.validate_user_input(combined_input)

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            specific_alert_ids=[request.alert_id] if request.alert_id else None,
            specific_indicators=request.indicators,
            query_text=request.context,
        )

        messages = [
            LLMMessage(role="system", content=THREAT_ANALYZER_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Alert ID: {request.alert_id}\n"
                    f"Indicators: {request.indicators}\n"
                    f"Context: {request.context}\n"
                    f"Authorized Intelligence & Telemetry Records:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"threat_summary": raw_output, "indicators_analyzed": [], "stix_correlations": []}

        sanitized_summary, verified_ids, _, score = (
            CyberAIFoundationGuardrails.sanitize_output(
                data.get("threat_summary", raw_output), set(auth_map.keys())
            )
        )

        sources = _build_source_references(verified_ids, auth_map)

        indicators_list = [
            IndicatorAnalysis(**item) for item in data.get("indicators_analyzed", [])
        ]

        await record_audit_log(
            action="AI_THREAT_ANALYSIS",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="THREAT_ANALYZER",
            details={
                "alert_id": request.alert_id,
                "indicators_count": len(request.indicators or []),
                "threat_level": data.get("threat_level", "MEDIUM"),
            },
            db=db,
        )

        return ThreatAnalyzerResponse(
            threat_summary=sanitized_summary,
            indicators_analyzed=indicators_list,
            stix_correlations=sources,
            threat_level=data.get("threat_level", "MEDIUM"),
            uncertainty_notes=data.get("uncertainty_notes", "Attribution subject to corroboration."),
            confidence=data.get("confidence", "HIGH" if score > 0.7 else "MEDIUM"),
            cited_sources=sources,
        )


# -------------------------------------------------------------------------
# 3. Incident Summariser Service
# -------------------------------------------------------------------------

class IncidentSummarizerService:
    @staticmethod
    async def summarize(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: IncidentSummarizerRequest,
        actor_email: Optional[str] = None,
    ) -> IncidentSummarizerResponse:
        PromptInjectionDetector.validate_user_input(request.case_id)

        # 1. Enforce tenant isolation: verify case belongs to requesting tenant
        stmt = select(IncidentCase).where(
            and_(
                IncidentCase.tenant_id == tenant_id,
                (IncidentCase.case_id == request.case_id) | (IncidentCase.case_number == request.case_id),
            )
        )
        case_res = await db.execute(stmt)
        case_obj = case_res.scalar_one_or_none()
        if not case_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident case '{request.case_id}' was not found in authorized tenant records.",
            )

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            specific_case_ids=[case_obj.case_id, case_obj.case_number],
            specific_alert_ids=case_obj.alerts_linked or [],
        )

        messages = [
            LLMMessage(role="system", content=INCIDENT_SUMMARISER_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Case Number: {case_obj.case_number}\n"
                    f"Title: {case_obj.title}\n"
                    f"Severity: {case_obj.severity}\n"
                    f"Phase: {case_obj.nist_phase}\n"
                    f"Authorized Evidence & Alerts:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"executive_summary": raw_output, "incident_timeline": [], "key_findings": []}

        sanitized_summary, verified_ids, _, _ = CyberAIFoundationGuardrails.sanitize_output(
            data.get("executive_summary", raw_output), set(auth_map.keys())
        )

        timeline = [TimelineEvent(**ev) for ev in data.get("incident_timeline", [])]
        sources = _build_source_references(verified_ids, auth_map)

        await record_audit_log(
            action="AI_INCIDENT_SUMMARY_GENERATED",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="INCIDENT_CASE",
            resource_id=case_obj.case_id,
            details={"case_number": case_obj.case_number, "timeline_events": len(timeline)},
            db=db,
        )

        return IncidentSummarizerResponse(
            case_id=case_obj.case_id,
            case_number=case_obj.case_number,
            executive_summary=sanitized_summary,
            incident_timeline=timeline,
            evidence_sources=sources,
            nist_phase=case_obj.nist_phase,
            key_findings=data.get("key_findings", []),
            closure_ready=data.get("closure_ready", False),
            confidence=data.get("confidence", "HIGH"),
        )


# -------------------------------------------------------------------------
# 4. Root Cause Analysis Service
# -------------------------------------------------------------------------

class RootCauseAnalysisService:
    @staticmethod
    async def analyze(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: RootCauseAnalysisRequest,
        actor_email: Optional[str] = None,
    ) -> RootCauseAnalysisResponse:
        combined = f"{request.case_id} {request.additional_context or ''}"
        PromptInjectionDetector.validate_user_input(combined)

        stmt = select(IncidentCase).where(
            and_(
                IncidentCase.tenant_id == tenant_id,
                (IncidentCase.case_id == request.case_id) | (IncidentCase.case_number == request.case_id),
            )
        )
        case_res = await db.execute(stmt)
        case_obj = case_res.scalar_one_or_none()
        if not case_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Incident case '{request.case_id}' was not found in authorized tenant records.",
            )

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            specific_case_ids=[case_obj.case_id],
            specific_alert_ids=case_obj.alerts_linked or [],
            query_text=request.additional_context,
        )

        messages = [
            LLMMessage(role="system", content=ROOT_CAUSE_ANALYSIS_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Case: {case_obj.case_number} - {case_obj.title}\n"
                    f"Additional Context: {request.additional_context or 'None'}\n"
                    f"Authorized Case Evidence:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"primary_root_cause_hypothesis": raw_output, "verified_facts": [], "hypotheses": []}

        sanitized_cause, verified_ids, _, _ = CyberAIFoundationGuardrails.sanitize_output(
            data.get("primary_root_cause_hypothesis", raw_output), set(auth_map.keys())
        )

        facts = [VerifiedFact(**f) for f in data.get("verified_facts", [])]
        hypotheses = [Hypothesis(**h) for h in data.get("hypotheses", [])]
        missing = [MissingEvidenceItem(**m) for m in data.get("missing_evidence", [])]
        sources = _build_source_references(verified_ids, auth_map)

        await record_audit_log(
            action="AI_ROOT_CAUSE_ANALYSIS",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="INCIDENT_CASE",
            resource_id=case_obj.case_id,
            details={"case_number": case_obj.case_number, "verified_facts_count": len(facts)},
            db=db,
        )

        return RootCauseAnalysisResponse(
            case_id=case_obj.case_id,
            verified_facts=facts,
            hypotheses=hypotheses,
            missing_evidence=missing,
            primary_root_cause_hypothesis=sanitized_cause,
            confidence_level=data.get("confidence_level", "MEDIUM"),
            cited_sources=sources,
        )


# -------------------------------------------------------------------------
# 5. Threat Hunting Assistant Service
# -------------------------------------------------------------------------

class ThreatHuntingService:
    @staticmethod
    async def formulate_hunt(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: ThreatHuntingRequest,
        actor_email: Optional[str] = None,
    ) -> ThreatHuntingResponse:
        PromptInjectionDetector.validate_user_input(request.hypothesis_focus)

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            query_text=request.hypothesis_focus,
        )

        messages = [
            LLMMessage(role="system", content=THREAT_HUNTING_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Hypothesis Focus: {request.hypothesis_focus}\n"
                    f"Target Techniques: {request.target_techniques or 'Any relevant'}\n"
                    f"Authorized Tenant Telemetry & Assets:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"hunting_hypotheses": [], "recommended_queries": [], "telemetry_sources_required": []}

        hyps = [HuntingHypothesis(**h) for h in data.get("hunting_hypotheses", [])]
        queries = [HuntingQuery(**q) for q in data.get("recommended_queries", [])]

        await record_audit_log(
            action="AI_THREAT_HUNTING_ASSISTANT",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="THREAT_HUNTING",
            details={"focus": request.hypothesis_focus, "queries_generated": len(queries)},
            db=db,
        )

        return ThreatHuntingResponse(
            hunting_hypotheses=hyps,
            recommended_queries=queries,
            telemetry_sources_required=data.get("telemetry_sources_required", []),
            prioritized_investigation_steps=data.get("prioritized_investigation_steps", []),
            confidence=data.get("confidence", "HIGH"),
        )


# -------------------------------------------------------------------------
# 6. Remediation Generator Service
# -------------------------------------------------------------------------

class RemediationGeneratorService:
    @staticmethod
    async def generate(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: RemediationGeneratorRequest,
        actor_email: Optional[str] = None,
    ) -> RemediationGeneratorResponse:
        combined = f"{request.finding_id or ''} {request.cve_id or ''} {request.asset_id or ''}"
        PromptInjectionDetector.validate_user_input(combined)

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            specific_finding_ids=[request.finding_id] if request.finding_id else None,
            specific_cve_ids=[request.cve_id] if request.cve_id else None,
            specific_asset_ids=[request.asset_id] if request.asset_id else None,
        )

        # Enforce grounding: if finding_id or asset_id was requested but not found in tenant records
        if request.finding_id and request.finding_id not in auth_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vulnerability finding '{request.finding_id}' not found in authorized tenant inventory.",
            )

        messages = [
            LLMMessage(role="system", content=REMEDIATION_GENERATOR_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Finding ID: {request.finding_id}\n"
                    f"CVE ID: {request.cve_id}\n"
                    f"Asset ID: {request.asset_id}\n"
                    f"Authorized Finding & Asset Context:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"remediation_plan": raw_output, "draft_commands": [], "draft_scripts": []}

        sanitized_plan, _, _, _ = CyberAIFoundationGuardrails.sanitize_output(
            data.get("remediation_plan", raw_output), set(auth_map.keys())
        )

        commands = [DraftCommand(**cmd) for cmd in data.get("draft_commands", [])]
        scripts = [DraftScript(**sc) for sc in data.get("draft_scripts", [])]

        # Register pending human approval requirement
        approval_id = f"AI-APP-{uuid.uuid4().hex[:8].upper()}"
        approval_token = f"APPROVAL-TOKEN-{uuid.uuid4().hex[:12].upper()}"

        approval_record = AIActionApproval(
            approval_id=approval_id,
            tenant_id=tenant_id,
            capability="remediation_generator",
            action_type="EXECUTE_REMEDIATION",
            target_id=request.finding_id or request.asset_id or request.cve_id,
            description=f"Automated remediation commands for {request.finding_id or request.cve_id or 'Finding'}",
            recommended_action={
                "commands": [c.model_dump() for c in commands],
                "scripts": [s.model_dump() for s in scripts],
                "plan": sanitized_plan,
            },
            is_draft=True,
            draft_watermark=CyberAIFoundationGuardrails.DRAFT_WATERMARK,
            status="PENDING",
            requested_by=actor_email or "AI_REMEDIATION_SERVICE",
            approval_token=approval_token,
            created_at=datetime.now(timezone.utc),
        )
        db.add(approval_record)
        await db.commit()

        await record_audit_log(
            action="AI_REMEDIATION_DRAFT_GENERATED",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="REMEDIATION",
            resource_id=approval_id,
            approval_reference=approval_token,
            details={"commands_count": len(commands), "scripts_count": len(scripts)},
            db=db,
        )

        return RemediationGeneratorResponse(
            finding_id=request.finding_id,
            cve_id=request.cve_id,
            asset_id=request.asset_id,
            remediation_plan=sanitized_plan,
            draft_commands=commands,
            draft_scripts=scripts,
            risk_level=data.get("risk_level", "HIGH"),
            requires_human_approval=True,
            is_draft=True,
            draft_watermark=CyberAIFoundationGuardrails.DRAFT_WATERMARK,
            approval_id=approval_id,
            approval_token=approval_token,
            confidence=data.get("confidence", "HIGH"),
        )


# -------------------------------------------------------------------------
# 7. Attack Path Prediction Service
# -------------------------------------------------------------------------

class AttackPathPredictionService:
    @staticmethod
    async def predict(
        db: AsyncSession,
        tenant_id: str,
        user_roles: List[str],
        request: AttackPathPredictionRequest,
        actor_email: Optional[str] = None,
    ) -> AttackPathPredictionResponse:
        combined = f"{request.target_asset_id or ''} {request.scenario or ''}"
        PromptInjectionDetector.validate_user_input(combined)

        context_str, auth_map = await AuthorizedRetriever.retrieve_records(
            db=db,
            tenant_id=tenant_id,
            user_roles=user_roles,
            specific_asset_ids=[request.target_asset_id] if request.target_asset_id else None,
            query_text=request.scenario,
        )

        # Enforce that target asset exists in tenant if specifically requested
        if request.target_asset_id and request.target_asset_id not in auth_map:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Target asset '{request.target_asset_id}' not found in authorized tenant inventory.",
            )

        messages = [
            LLMMessage(role="system", content=ATTACK_PATH_PREDICTION_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    f"Tenant ID: {tenant_id}\n"
                    f"Target Asset: {request.target_asset_id or 'Crown Jewels'}\n"
                    f"Scenario: {request.scenario or 'Standard Perimeter Penetration'}\n"
                    f"Authorized Tenant Assets, Findings & Telemetry:\n{context_str}"
                ),
            ),
        ]

        raw_output = await llm_client.generate(messages, json_mode=True)
        try:
            data = json.loads(raw_output)
        except Exception:
            data = {"scenario": raw_output, "predicted_paths": [], "assumptions": []}

        sanitized_scenario, verified_ids, _, _ = CyberAIFoundationGuardrails.sanitize_output(
            data.get("scenario", raw_output), set(auth_map.keys())
        )

        steps = [AttackPathStep(**p) for p in data.get("predicted_paths", [])]
        sources = _build_source_references(verified_ids, auth_map)

        await record_audit_log(
            action="AI_ATTACK_PATH_PREDICTED",
            tenant_id=tenant_id,
            actor_email=actor_email,
            resource_type="ATTACK_PATH",
            details={
                "target_asset_id": request.target_asset_id,
                "steps_count": len(steps),
                "risk_rating": data.get("overall_risk_rating", "HIGH"),
            },
            db=db,
        )

        return AttackPathPredictionResponse(
            scenario=sanitized_scenario,
            predicted_paths=steps,
            supporting_evidence=sources,
            assumptions=data.get("assumptions", []),
            limitations=data.get("limitations", []),
            critical_assets_at_risk=data.get("critical_assets_at_risk", []),
            overall_risk_rating=data.get("overall_risk_rating", "HIGH"),
            confidence=data.get("confidence", "MEDIUM"),
        )


# -------------------------------------------------------------------------
# Human-in-the-Loop Approval Workflow Service
# -------------------------------------------------------------------------

class ApprovalWorkflowService:
    @staticmethod
    async def list_approvals(
        db: AsyncSession,
        tenant_id: str,
        status_filter: Optional[str] = None,
    ) -> List[AIApprovalItem]:
        stmt = select(AIActionApproval).where(AIActionApproval.tenant_id == tenant_id)
        if status_filter and status_filter.upper() != "ALL":
            stmt = stmt.where(AIActionApproval.status == status_filter.upper())
        stmt = stmt.order_by(AIActionApproval.created_at.desc())
        res = await db.execute(stmt)
        items = res.scalars().all()
        return [
            AIApprovalItem(
                approval_id=i.approval_id,
                tenant_id=i.tenant_id,
                capability=i.capability,
                action_type=i.action_type,
                target_id=i.target_id,
                description=i.description,
                recommended_action=i.recommended_action or {},
                is_draft=i.is_draft,
                draft_watermark=i.draft_watermark,
                status=i.status,
                requested_by=i.requested_by,
                reviewed_by=i.reviewed_by,
                decision_reason=i.decision_reason,
                approval_token=i.approval_token,
                action_reference=i.action_reference,
                created_at=i.created_at.isoformat() if i.created_at else "",
                decided_at=i.decided_at.isoformat() if i.decided_at else None,
                executed_at=i.executed_at.isoformat() if i.executed_at else None,
            )
            for i in items
        ]

    @staticmethod
    async def decide_approval(
        db: AsyncSession,
        tenant_id: str,
        approval_id: str,
        request: ApprovalDecisionRequest,
    ) -> ApprovalActionResponse:
        stmt = select(AIActionApproval).where(
            and_(
                AIActionApproval.tenant_id == tenant_id,
                AIActionApproval.approval_id == approval_id,
            )
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Approval request '{approval_id}' not found for tenant.",
            )

        if record.approval_token != request.approval_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security Guardrail Violation: Human approval token mismatch.",
            )

        norm_decision = request.decision.strip().upper()
        if norm_decision not in ["APPROVED", "REJECTED"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Decision must be either 'APPROVED' or 'REJECTED'.",
            )

        now = datetime.now(timezone.utc)
        record.status = norm_decision
        record.reviewed_by = request.reviewer_email
        record.decision_reason = request.decision_reason
        record.decided_at = now
        await db.commit()

        await record_audit_log(
            action=f"AI_ACTION_{norm_decision}",
            tenant_id=tenant_id,
            actor_email=request.reviewer_email,
            resource_type="AI_ACTION_APPROVAL",
            resource_id=approval_id,
            approval_reference=request.approval_token,
            details={"decision": norm_decision, "reason": request.decision_reason},
            db=db,
        )

        return ApprovalActionResponse(
            approval_id=approval_id,
            status=norm_decision,
            capability=record.capability,
            action_type=record.action_type,
            reviewed_by=request.reviewer_email,
            decision_reason=request.decision_reason,
            decided_at=now.isoformat(),
            message=f"AI action {norm_decision.lower()} successfully by human reviewer.",
        )

    @staticmethod
    async def execute_approved_action(
        db: AsyncSession,
        tenant_id: str,
        approval_id: str,
        approval_token: str,
        operator_email: str,
    ) -> Dict[str, Any]:
        stmt = select(AIActionApproval).where(
            and_(
                AIActionApproval.tenant_id == tenant_id,
                AIActionApproval.approval_id == approval_id,
            )
        )
        res = await db.execute(stmt)
        record = res.scalar_one_or_none()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Approval request '{approval_id}' not found for tenant.",
            )

        # BACKEND ENFORCEMENT OF HUMAN-IN-THE-LOOP APPROVAL
        SensitiveActionGuardrail.enforce_execution_preconditions(
            action_type=record.action_type,
            approval_status=record.status,
            reviewer_email=record.reviewed_by,
        )

        now = datetime.now(timezone.utc)
        record.status = "EXECUTED"
        record.executed_at = now
        record.action_reference = f"EXEC-{uuid.uuid4().hex[:8].upper()}"
        await db.commit()

        await record_audit_log(
            action="AI_ACTION_EXECUTED",
            tenant_id=tenant_id,
            actor_email=operator_email,
            resource_type="AI_ACTION_APPROVAL",
            resource_id=approval_id,
            approval_reference=record.action_reference,
            details={"action_type": record.action_type, "executed_by": operator_email},
            db=db,
        )

        return {
            "success": True,
            "status": "EXECUTED",
            "approval_id": approval_id,
            "action_type": record.action_type,
            "action_reference": record.action_reference,
            "executed_at": now.isoformat(),
            "message": f"Approved AI action '{record.action_type}' safely dispatched under human supervision.",
        }

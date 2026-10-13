from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------------------
# Common Schemas
# -------------------------------------------------------------------------

class SourceReference(BaseModel):
    record_id: str
    record_type: str
    title: str
    verified: bool = True


# -------------------------------------------------------------------------
# 1. SOC Copilot Schemas
# -------------------------------------------------------------------------

class SOCCopilotRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000)
    alert_ids: Optional[List[str]] = None
    case_ids: Optional[List[str]] = None


class SOCCopilotResponse(BaseModel):
    answer: str
    cited_sources: List[SourceReference] = []
    suggested_followups: List[str] = []
    confidence: str = "HIGH"
    grounding_score: float = 1.0
    is_draft: bool = True
    draft_watermark: str = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"


# -------------------------------------------------------------------------
# 2. Threat Analyzer Schemas
# -------------------------------------------------------------------------

class ThreatAnalyzerRequest(BaseModel):
    alert_id: Optional[str] = None
    indicators: Optional[List[str]] = None
    context: Optional[str] = None


class IndicatorAnalysis(BaseModel):
    indicator: str
    type: str
    threat_level: str
    confidence: int


class ThreatAnalyzerResponse(BaseModel):
    threat_summary: str
    indicators_analyzed: List[IndicatorAnalysis] = []
    stix_correlations: List[SourceReference] = []
    threat_level: str = "MEDIUM"
    uncertainty_notes: str = ""
    confidence: str = "HIGH"
    cited_sources: List[SourceReference] = []


# -------------------------------------------------------------------------
# 3. Incident Summariser Schemas
# -------------------------------------------------------------------------

class IncidentSummarizerRequest(BaseModel):
    case_id: str


class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    source_id: str


class IncidentSummarizerResponse(BaseModel):
    case_id: str
    case_number: str
    executive_summary: str
    incident_timeline: List[TimelineEvent] = []
    evidence_sources: List[SourceReference] = []
    nist_phase: str
    key_findings: List[str] = []
    closure_ready: bool = False
    confidence: str = "HIGH"


# -------------------------------------------------------------------------
# 4. Root Cause Analysis Schemas
# -------------------------------------------------------------------------

class RootCauseAnalysisRequest(BaseModel):
    case_id: str
    additional_context: Optional[str] = None


class VerifiedFact(BaseModel):
    fact: str
    source_id: str


class Hypothesis(BaseModel):
    hypothesis: str
    likelihood: str
    supporting_evidence: List[str] = []


class MissingEvidenceItem(BaseModel):
    item: str
    importance: str


class RootCauseAnalysisResponse(BaseModel):
    case_id: str
    verified_facts: List[VerifiedFact] = []
    hypotheses: List[Hypothesis] = []
    missing_evidence: List[MissingEvidenceItem] = []
    primary_root_cause_hypothesis: str
    confidence_level: str = "MEDIUM"
    cited_sources: List[SourceReference] = []


# -------------------------------------------------------------------------
# 5. Threat Hunting Assistant Schemas
# -------------------------------------------------------------------------

class ThreatHuntingRequest(BaseModel):
    hypothesis_focus: str
    target_techniques: Optional[List[str]] = None


class HuntingHypothesis(BaseModel):
    hypothesis: str
    tactic: str
    technique_id: str


class HuntingQuery(BaseModel):
    format: str  # SIGMA, WAZUH, SPLUNK
    title: str
    query: str


class ThreatHuntingResponse(BaseModel):
    hunting_hypotheses: List[HuntingHypothesis] = []
    recommended_queries: List[HuntingQuery] = []
    telemetry_sources_required: List[str] = []
    prioritized_investigation_steps: List[str] = []
    confidence: str = "HIGH"


# -------------------------------------------------------------------------
# 6. Remediation Generator Schemas
# -------------------------------------------------------------------------

class RemediationGeneratorRequest(BaseModel):
    finding_id: Optional[str] = None
    cve_id: Optional[str] = None
    asset_id: Optional[str] = None


class DraftCommand(BaseModel):
    step: int
    description: str
    command: str
    is_draft: bool = True


class DraftScript(BaseModel):
    language: str
    filename: str
    script_content: str
    is_draft: bool = True


class RemediationGeneratorResponse(BaseModel):
    finding_id: Optional[str] = None
    cve_id: Optional[str] = None
    asset_id: Optional[str] = None
    remediation_plan: str
    draft_commands: List[DraftCommand] = []
    draft_scripts: List[DraftScript] = []
    risk_level: str = "HIGH"
    requires_human_approval: bool = True
    is_draft: bool = True
    draft_watermark: str = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"
    approval_id: str
    approval_token: str
    confidence: str = "HIGH"


# -------------------------------------------------------------------------
# 7. Attack Path Prediction Schemas
# -------------------------------------------------------------------------

class AttackPathPredictionRequest(BaseModel):
    target_asset_id: Optional[str] = None
    scenario: Optional[str] = None


class AttackPathStep(BaseModel):
    step: int
    source_asset: str
    target_asset: str
    technique: str
    evidence_id: str
    likelihood: str


class AttackPathPredictionResponse(BaseModel):
    scenario: str
    predicted_paths: List[AttackPathStep] = []
    supporting_evidence: List[SourceReference] = []
    assumptions: List[str] = []
    limitations: List[str] = []
    critical_assets_at_risk: List[str] = []
    overall_risk_rating: str = "HIGH"
    confidence: str = "MEDIUM"


# -------------------------------------------------------------------------
# Human-in-the-Loop Approval Schemas
# -------------------------------------------------------------------------

class ApprovalDecisionRequest(BaseModel):
    decision: str  # APPROVED, REJECTED
    reviewer_email: str
    decision_reason: str
    approval_token: str


class ApprovalActionResponse(BaseModel):
    approval_id: str
    status: str
    capability: str
    action_type: str
    reviewed_by: Optional[str] = None
    decision_reason: Optional[str] = None
    decided_at: Optional[str] = None
    message: str


class ApprovalExecuteRequest(BaseModel):
    approval_token: str
    operator_email: str


class AIApprovalItem(BaseModel):
    approval_id: str
    tenant_id: str
    capability: str
    action_type: str
    target_id: Optional[str] = None
    description: Optional[str] = None
    recommended_action: Dict[str, Any] = {}
    is_draft: bool = True
    draft_watermark: str = "DRAFT_SUBJECT_TO_HUMAN_APPROVAL"
    status: str
    requested_by: str
    reviewed_by: Optional[str] = None
    decision_reason: Optional[str] = None
    approval_token: str
    action_reference: Optional[str] = None
    created_at: str
    decided_at: Optional[str] = None
    executed_at: Optional[str] = None

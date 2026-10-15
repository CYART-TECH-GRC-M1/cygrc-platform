"""Schema definitions and validation engine for CyGRC Playbooks.

Enforces:
1. Complete schema for metadata, inputs, ordered workflow steps, permissions, approvals,
   evidence requirements, retries, and conditions.
2. Step classification into:
   - READ_ONLY
   - REVERSIBLE_LOW_RISK
   - SENSITIVE_DISRUPTIVE
   - DESTRUCTIVE
3. Human approval requirements for sensitive or destructive operations.
4. Red Team sandboxing restrictions (never target real systems outside authorized scope).
5. Mobile assessment stub validation (explicit stub status, no fabricated scans).
6. Strict prevention of arbitrary commands, eval, or unrestricted shell scripts.
"""
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


class StepClassification(str, Enum):
    READ_ONLY = "READ_ONLY"
    REVERSIBLE_LOW_RISK = "REVERSIBLE_LOW_RISK"
    SENSITIVE_DISRUPTIVE = "SENSITIVE_DISRUPTIVE"
    DESTRUCTIVE = "DESTRUCTIVE"


class PlaybookDiscipline(str, Enum):
    SOC = "SOC"
    VAPT = "VAPT"
    DFIR = "DFIR"
    RED_TEAM = "RED_TEAM"


class PlaybookStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    STUB = "STUB"


class StepRetryPolicy(BaseModel):
    max_retries: int = Field(default=1, ge=0, le=5)
    backoff_seconds: float = Field(default=1.0, ge=0.1, le=60.0)


class StepEvidenceRequirements(BaseModel):
    record_evidence: bool = Field(default=False)
    evidence_type: Optional[str] = Field(default=None)
    require_hash: bool = Field(default=False)


# Approved registered action names — arbitrary or unrestricted command execution is strictly forbidden
APPROVED_PLAYBOOK_ACTIONS = {
    # SOC Actions
    "threat_intel_lookup",
    "alert_enrichment",
    "asset_criticality_lookup",
    "quarantine_host_simulation",
    "create_ir_case",
    "transition_case_status",
    "create_jira_ticket",
    "record_evidence_entry",
    "extract_email_iocs",
    "block_sender_domain",
    "purge_mailbox_items",
    "terminate_process_simulation",
    "dispatch_forensics_collection",
    "evaluate_ueba_baseline",
    "audit_log_query",
    "suspend_user_simulation",
    "correlate_tenant_alerts",
    "enforce_containment_perimeter",
    "generate_case_closure_summary",
    # VAPT Actions
    "validate_target_scope",
    "dispatch_web_zap_scan",
    "dispatch_nmap_port_discovery",
    "dispatch_openvas_cve_scan",
    "prioritize_vulnerabilities",
    "push_findings_to_jira",
    "feed_vapt_evidence_to_grc",
    "dispatch_api_fuzz_scan",
    "export_assessment_report",
    "verify_mobile_stub_notice",
    # DFIR Actions
    "validate_endpoint_reachability",
    "dispatch_velociraptor_collection",
    "compute_evidence_sha256",
    "commit_chain_of_custody_entry",
    "query_custody_timeline",
    "perform_memory_dump_analysis",
    "static_pe_analysis",
    "sandbox_detonation_simulation",
    "generate_stix_ioc_bundle",
    "verify_custody_integrity_seal",
    "export_forensic_audit_package",
    # Red Team Actions
    "validate_sandboxed_target",
    "execute_atomic_test_sandboxed",
    "verify_purple_team_detection",
    "record_atomic_execution_job",
    "cleanup_simulated_artifact",
    "generate_campaign_summary_report",
}


class StepApprovalConfig(BaseModel):
    required: bool = False
    role: str = "SOC Lead"
    justification_prompt: Optional[str] = None


class PlaybookStep(BaseModel):
    id: str = Field(..., pattern=r"^[a-zA-Z0-9_\-]+$")
    name: str = Field(..., min_length=3, max_length=255)
    action: str = Field(...)
    classification: StepClassification = Field(...)
    requires_approval: bool = Field(default=False)
    approval_role: str = Field(default="SOC Lead")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    input_mapping: Dict[str, str] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=60, ge=1, le=1800)
    retry_policy: StepRetryPolicy = Field(default_factory=StepRetryPolicy)
    evidence_requirements: StepEvidenceRequirements = Field(default_factory=StepEvidenceRequirements)
    ignore_failure: bool = Field(default=False)

    @field_validator("action")
    @classmethod
    def validate_action_not_arbitrary(cls, v: str) -> str:
        if v not in APPROVED_PLAYBOOK_ACTIONS:
            raise ValueError(
                f"Action '{v}' is not an approved registered action. "
                f"Arbitrary commands and unrestricted execution are strictly forbidden."
            )
        return v

    @model_validator(mode="after")
    def enforce_approval_for_sensitive_steps(self) -> "PlaybookStep":
        # Sensitive or destructive operations MUST require human approval
        if self.classification in (StepClassification.SENSITIVE_DISRUPTIVE, StepClassification.DESTRUCTIVE):
            self.requires_approval = True
        return self


class InputParameter(BaseModel):
    type: str = Field(default="string")  # string, integer, boolean, number, list, dict
    required: bool = Field(default=True)
    default: Optional[Any] = None
    description: Optional[str] = None
    pattern: Optional[str] = None
    enum: Optional[List[Any]] = None


class AuditMetadata(BaseModel):
    author: str = Field(..., min_length=2)
    created_at: str = Field(...)
    updated_at: str = Field(...)
    tags: List[str] = Field(default_factory=list)
    compliance_mappings: List[Dict[str, str]] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)


class PlaybookDefinition(BaseModel):
    id: str = Field(..., pattern=r"^[a-zA-Z0-9_\-]+$")
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    name: str = Field(..., min_length=3, max_length=255)
    discipline: PlaybookDiscipline = Field(...)
    status: PlaybookStatus = Field(default=PlaybookStatus.ACTIVE)
    description: str = Field(..., min_length=10)
    intended_use: str = Field(..., min_length=10)
    preconditions: List[Dict[str, Any]] = Field(default_factory=list)
    authorized_target_types: List[str] = Field(..., min_length=1)
    required_permissions: List[str] = Field(default_factory=lambda: ["playbook:execute"])
    inputs: Dict[str, InputParameter] = Field(default_factory=dict)
    steps: List[PlaybookStep] = Field(..., min_length=1)
    success_conditions: List[str] = Field(default_factory=lambda: ["all_required_steps_succeeded"])
    failure_conditions: List[str] = Field(default_factory=lambda: ["any_critical_step_failed"])
    audit_metadata: AuditMetadata = Field(...)

    @model_validator(mode="after")
    def validate_playbook_integrity(self) -> "PlaybookDefinition":
        # 1. Unique step IDs
        step_ids = [s.id for s in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError(f"Playbook '{self.id}' contains duplicate step IDs: {step_ids}")

        # 2. Red team playbooks must strictly use sandboxed targets
        if self.discipline == PlaybookDiscipline.RED_TEAM:
            disallowed_targets = {"production", "all", "internet", "external_ip"}
            for t in self.authorized_target_types:
                if t.lower() in disallowed_targets or not any(
                    valid in t.lower() for valid in ["sandbox", "test", "lab", "vm", "staging", "target"]
                ):
                    raise ValueError(
                        f"Red Team playbook '{self.id}' cannot target '{t}'. "
                        f"Red Team playbooks must use approved sandboxed test actions and target types."
                    )

        # 3. Mobile assessment stub validation
        if self.id in ("pb-vapt-mobile-stub", "vapt_mobile_stub", "mobile_assessment_stub") or "mobile" in self.id.lower():
            if self.status != PlaybookStatus.STUB and "stub" not in self.intended_use.lower():
                raise ValueError(
                    f"Mobile assessment playbook '{self.id}' must be explicitly identified as STUB "
                    f"and must not claim to perform real mobile scans."
                )

        return self


def validate_playbook_dict(data: Dict[str, Any]) -> PlaybookDefinition:
    """Validates raw parsed YAML dict against the Playbook schema."""
    # Guard against dangerous YAML / command keys
    forbidden_keys = {"exec", "eval", "command", "shell", "subprocess", "bash", "sh", "system"}
    
    def check_keys(obj: Any):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.lower() in forbidden_keys:
                    raise ValueError(f"Dangerous key '{k}' detected. Unrestricted commands are forbidden.")
                check_keys(v)
        elif isinstance(obj, list):
            for item in obj:
                check_keys(item)

    check_keys(data)
    return PlaybookDefinition.model_validate(data)


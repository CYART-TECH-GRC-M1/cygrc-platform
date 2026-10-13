import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Boolean
from backend.core.database import Base


class PlaybookExecution(Base):
    """
    Durable Playbook Execution Record.
    Tracks end-to-end execution lifecycle, per-step results, approval states, and evidence references.
    """
    __tablename__ = "playbook_executions"

    execution_id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"PB-EXEC-{uuid.uuid4().hex[:12].upper()}"
    )
    tenant_id = Column(String(36), nullable=False, index=True)
    playbook_id = Column(String(100), nullable=False, index=True)
    playbook_version = Column(String(50), nullable=False)
    playbook_name = Column(String(255), nullable=False)
    discipline = Column(String(50), nullable=False)  # SOC, VAPT, DFIR, RED_TEAM

    actor_id = Column(String(255), nullable=False)
    actor_email = Column(String(255), nullable=True)
    actor_role = Column(String(100), nullable=True)

    target = Column(String(255), nullable=True)
    target_type = Column(String(50), nullable=True)

    related_alert_id = Column(String(255), nullable=True)
    related_case_id = Column(String(255), nullable=True)
    related_finding_id = Column(String(255), nullable=True)
    related_campaign_id = Column(String(255), nullable=True)

    inputs = Column(JSON, nullable=False, default=dict)

    current_step_id = Column(String(100), nullable=True)
    current_step_index = Column(Integer, nullable=False, default=0)
    total_steps = Column(Integer, nullable=False, default=0)

    # Status: PENDING, RUNNING, WAITING_FOR_APPROVAL, COMPLETED, FAILED, CANCELLED, TIMED_OUT
    status = Column(String(50), nullable=False, default="PENDING", index=True)

    step_results = Column(JSON, nullable=False, default=list)
    evidence_references = Column(JSON, nullable=False, default=list)
    approval_state = Column(JSON, nullable=False, default=dict)
    errors = Column(JSON, nullable=False, default=list)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)


class PlaybookApprovalRecord(Base):
    """
    Persistent Human-in-the-Loop Playbook Step Approval Record.
    Mandatory gate before sensitive or destructive actions can execute.
    """
    __tablename__ = "playbook_step_approvals"

    approval_id = Column(
        String(64),
        primary_key=True,
        default=lambda: f"PB-APP-{uuid.uuid4().hex[:12].upper()}"
    )
    execution_id = Column(String(64), nullable=False, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    playbook_id = Column(String(100), nullable=False, index=True)
    playbook_version = Column(String(50), nullable=False)
    step_id = Column(String(100), nullable=False)
    step_name = Column(String(255), nullable=False)
    step_classification = Column(String(50), nullable=False)  # SENSITIVE_DISRUPTIVE, DESTRUCTIVE
    action_type = Column(String(100), nullable=False)
    target = Column(String(255), nullable=True)

    # Status: PENDING, APPROVED, REJECTED
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    required_role = Column(String(100), nullable=False, default="SOC Lead")
    requested_by = Column(String(255), nullable=False)
    reviewed_by = Column(String(255), nullable=True)
    decision = Column(String(50), nullable=True)  # APPROVED, REJECTED
    decision_reason = Column(Text, nullable=True)
    approval_token = Column(String(255), nullable=False, unique=True, index=True)
    action_scope = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    decided_at = Column(DateTime, nullable=True)


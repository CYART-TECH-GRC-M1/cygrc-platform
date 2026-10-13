import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, Boolean, JSON
from backend.core.database import Base


class AIActionApproval(Base):
    """
    Persistent Human-in-the-Loop AI Action Approval record.
    Enforces backend approval checks before any sensitive AI recommendation can be executed.
    """
    __tablename__ = "ai_action_approvals"

    approval_id = Column(String(36), primary_key=True, default=lambda: f"AI-APP-{uuid.uuid4().hex[:8].upper()}")
    tenant_id = Column(String(36), nullable=False, index=True)
    capability = Column(String(100), nullable=False, default="remediation")
    action_type = Column(String(100), nullable=False)  # EXECUTE_REMEDIATION, ISOLATE_HOST, BLOCK_USER, DELETE_FILE, EXECUTE_EXPLOIT, LAUNCH_SCAN, CLOSE_INCIDENT
    target_id = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    recommended_action = Column(JSON, nullable=True, default=dict)
    is_draft = Column(Boolean, nullable=False, default=True)
    draft_watermark = Column(String(255), nullable=False, default="DRAFT_SUBJECT_TO_HUMAN_APPROVAL")
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED, EXECUTED
    requested_by = Column(String(255), nullable=False, default="CYBER_AI_SERVICE")
    reviewed_by = Column(String(255), nullable=True)
    decision_reason = Column(Text, nullable=True)
    approval_token = Column(String(255), nullable=False, unique=True, index=True)
    action_reference = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    decided_at = Column(DateTime, nullable=True)
    executed_at = Column(DateTime, nullable=True)

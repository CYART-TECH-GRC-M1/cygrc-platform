import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer, Float
from backend.core.database import Base


class RedTeamCampaign(Base):
    """
    Persistent Red Team Campaign with authorized scope, target inventory,
    approval lifecycle, and execution tracking.
    """
    __tablename__ = "red_team_campaigns"

    campaign_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    authorized_scope = Column(JSON, nullable=True, default=dict)  # {"environments": [...], "allowed_ip_ranges": [...], "allowed_hosts": [...]}
    approved_targets = Column(JSON, nullable=True, default=list)  # list of authorized asset IDs
    status = Column(String(50), nullable=False, default="ACTIVE")  # PLANNING, READY, ACTIVE, PAUSED, COMPLETED, CANCELLED, FAILED
    approval_status = Column(String(50), nullable=False, default="APPROVED")  # PENDING_APPROVAL, APPROVED, REJECTED, EXPIRED
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    operator_id = Column(String(255), nullable=True)
    schedule_type = Column(String(50), nullable=False, default="MANUAL")  # MANUAL, SCHEDULED
    scheduled_at = Column(DateTime, nullable=True)
    techniques_tested = Column(JSON, nullable=True, default=list)  # list of MITRE technique IDs
    technique_catalogue = Column(JSON, nullable=True, default=list)  # full planned technique specifications
    coverage_score = Column(String(20), nullable=True, default="0%")
    execution_summary = Column(JSON, nullable=True, default=dict)  # counts of planned, executed, detected, gaps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RedTeamExecutionJob(Base):
    """
    Persistent execution job within a Red Team campaign or standalone test.
    """
    __tablename__ = "red_team_execution_jobs"

    job_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=True, index=True)
    engine = Column(String(50), nullable=False, default="ATOMIC_RED_TEAM")  # ATOMIC_RED_TEAM, CALDERA
    technique_id = Column(String(50), nullable=False, index=True)
    technique_name = Column(String(255), nullable=False)
    tactic_id = Column(String(50), nullable=True)
    target_asset_id = Column(String(255), nullable=False, index=True)
    target_ip = Column(String(100), nullable=True)
    target_hostname = Column(String(255), nullable=True)
    operator_id = Column(String(255), nullable=True)
    status = Column(String(50), nullable=False, default="PENDING")  # PENDING, RUNNING, EXECUTED, FAILED, CANCELLED, TIMEOUT
    exit_code = Column(Integer, nullable=True)
    output_log = Column(Text, nullable=True)
    error_log = Column(Text, nullable=True)
    execution_hash = Column(String(64), nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AtomicTestExecution(Base):
    """
    Persisted Atomic Red Team execution record replacing volatile in-memory history.
    """
    __tablename__ = "atomic_test_executions"

    execution_id = Column(String, primary_key=True, default=lambda: f"ART-{uuid.uuid4().hex[:8].upper()}")
    tenant_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=True, index=True)
    job_id = Column(String, nullable=True, index=True)
    technique_id = Column(String(50), nullable=False, index=True)
    technique_name = Column(String(255), nullable=False)
    test_guid = Column(String(100), nullable=True)
    target_asset_id = Column(String(255), nullable=False, index=True)
    executor = Column(String(50), nullable=False, default="powershell")
    command_executed = Column(Text, nullable=False)
    exit_code = Column(Integer, nullable=False, default=0)
    status = Column(String(50), nullable=False, default="SUCCESS")  # SUCCESS, FAILED, TIMEOUT, CANCELLED, BLOCKED
    execution_log = Column(Text, nullable=False)
    execution_hash = Column(String(64), nullable=False)
    telemetry_collected = Column(JSON, nullable=True, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)


class DetectionVerificationRecord(Base):
    """
    Correlates red team test executions with actual SOC alerts and telemetry.
    """
    __tablename__ = "detection_verification_records"

    verification_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=True, index=True)
    execution_id = Column(String, nullable=False, index=True)
    technique_id = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False, default="GAP")  # DETECTED, GAP, INCONCLUSIVE, MANUALLY_VERIFIED
    matched_alert_ids = Column(JSON, nullable=True, default=list)  # list of alert UUIDs from alerts table
    detection_rules_fired = Column(JSON, nullable=True, default=list)  # Sigma / Wazuh rules
    evidence_references = Column(JSON, nullable=True, default=dict)
    notes = Column(Text, nullable=True)
    verified_by = Column(String(255), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class CampaignReport(Base):
    """
    Persisted post-campaign report with coverage calculations and remediation backlog.
    """
    __tablename__ = "campaign_reports"

    report_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, index=True)
    campaign_id = Column(String, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    executive_summary = Column(Text, nullable=False)
    attack_matrix_version = Column(String(50), nullable=False, default="MITRE ATT&CK Enterprise v19.1")
    total_planned = Column(Integer, nullable=False, default=0)
    total_attempted = Column(Integer, nullable=False, default=0)
    total_executed = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    total_detected = Column(Integer, nullable=False, default=0)
    detection_gaps = Column(Integer, nullable=False, default=0)
    inconclusive = Column(Integer, nullable=False, default=0)
    planned_coverage_pct = Column(Float, nullable=False, default=0.0)
    execution_coverage_pct = Column(Float, nullable=False, default=0.0)
    detection_coverage_pct = Column(Float, nullable=False, default=0.0)
    gap_percentage = Column(Float, nullable=False, default=0.0)
    remediation_backlog = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

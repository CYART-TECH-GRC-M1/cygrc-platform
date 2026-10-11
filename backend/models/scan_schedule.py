import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text
from backend.core.database import Base


class ScanSchedule(Base):
    __tablename__ = "scan_schedules"

    schedule_id = Column(String(36), primary_key=True, default=lambda: f"SCHED-{uuid.uuid4().hex[:8].upper()}")
    tenant_id = Column(String(36), nullable=False, index=True)
    asset_id = Column(String(36), nullable=True, index=True)
    target = Column(String(255), nullable=False)
    scan_type = Column(String(50), nullable=False, default="NETWORK_NMAP")  # NETWORK_NMAP, WEB_ZAP, VULN_OPENVAS, FULL_VAPT
    frequency = Column(String(50), nullable=False, default="DAILY")  # ONCE, HOURLY, DAILY, WEEKLY, MONTHLY
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, PAUSED, CANCELLED, COMPLETED
    concurrency_limit = Column(Integer, default=2)
    next_run_at = Column(DateTime, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    last_status = Column(String(50), nullable=True)  # SUCCESS, FAILED, TIMEOUT
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class ScanJob(Base):
    __tablename__ = "scan_jobs"

    job_id = Column(String(36), primary_key=True, default=lambda: f"JOB-{uuid.uuid4().hex[:8].upper()}")
    schedule_id = Column(String(36), nullable=True, index=True)
    tenant_id = Column(String(36), nullable=False, index=True)
    asset_id = Column(String(36), nullable=True, index=True)
    target = Column(String(255), nullable=False)
    scan_type = Column(String(50), nullable=False, default="NETWORK_NMAP")
    status = Column(String(50), nullable=False, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED
    scanner_tool = Column(String(50), nullable=False, default="NMAP")  # NMAP, ZAP, OPENVAS
    parameters = Column(JSON, nullable=True, default=dict)
    raw_output = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    findings_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

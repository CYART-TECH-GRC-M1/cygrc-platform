import uuid
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, JSON, Index, Boolean

from backend.core.database import Base


class ForensicJob(Base):
    """Durable record of a forensic collection or analysis job."""

    __tablename__ = "forensic_jobs"

    job_id = Column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    tenant_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=False, index=True)
    case_id = Column(String(100), nullable=True, index=True)

    target = Column(String(500), nullable=False)
    tool = Column(String(50), nullable=False)
    operation = Column(
        String(50),
        nullable=False,
        default="COLLECTION",
    )
    artifact_name = Column(String(255), nullable=True)

    status = Column(
        String(20),
        nullable=False,
        default="QUEUED",
        index=True,
    )
    external_job_id = Column(String(255), nullable=True, index=True)

    parameters = Column(JSON, nullable=True)
    result_metadata = Column(JSON, nullable=True)

    error_message = Column(Text, nullable=True)

    cancellation_requested = Column(
        Boolean,
        nullable=False,
        default=False,
    )

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


Index(
    "ix_forensic_jobs_tenant_status",
    ForensicJob.tenant_id,
    ForensicJob.status,
)

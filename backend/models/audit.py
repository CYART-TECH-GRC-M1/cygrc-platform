import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.core.database import Base


class AuditLog(Base):
    __tablename__ = "activity_logs"

    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    actor_id = Column(String(36), nullable=True, index=True)
    actor_email = Column(String(255), nullable=True)
    actor_role = Column(String(100), nullable=True)
    action = Column(String(255), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(255), nullable=True)
    result = Column(String(50), nullable=False, default="SUCCESS")  # SUCCESS, DENIED, FAILURE
    correlation_id = Column(String(64), nullable=True, index=True)
    approval_reference = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

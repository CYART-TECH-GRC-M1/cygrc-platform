import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.core.database import Base


class IncidentCase(Base):
    __tablename__ = "incident_cases"

    case_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    case_number = Column(String(50), nullable=False, unique=True, index=True)
    title = Column(String(255), nullable=False)
    nist_phase = Column(
        String(100),
        nullable=False,
        default="DETECTION_ANALYSIS"
    )  # PREPARATION, DETECTION_ANALYSIS, CONTAINMENT_ERADICATION_RECOVERY, POST_INCIDENT_ACTIVITY
    severity = Column(String(50), nullable=False, default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="OPEN")  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    summary = Column(Text, nullable=True)
    assigned_analyst = Column(String(255), nullable=True)
    alerts_linked = Column(JSON, nullable=True, default=list)  # list of alert_ids
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

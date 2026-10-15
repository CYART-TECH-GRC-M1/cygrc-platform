import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
import enum
from backend.core.database import Base


class AlertSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, enum.Enum):
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


class Alert(Base):
    __tablename__ = "alerts"

    alert_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    title = Column(String(255), nullable=False)
    source = Column(String(100), nullable=False, default="Wazuh")
    severity = Column(String(50), nullable=False, default=AlertSeverity.MEDIUM.value)
    status = Column(String(50), nullable=False, default=AlertStatus.NEW.value)
    description = Column(Text, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

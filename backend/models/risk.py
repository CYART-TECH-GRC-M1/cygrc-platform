import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


class RiskRegister(Base):
    """Persistent risk register for GRC compliance tracking."""
    __tablename__ = "risk_register"

    risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(255), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    description = Column(Text, nullable=True)
    likelihood = Column(Integer, nullable=False, default=1)
    impact = Column(Integer, nullable=False, default=1)
    risk_score = Column(Integer, nullable=False, default=1)
    status = Column(String(64), nullable=False, default="ACTIVE")
    source = Column(String(128), nullable=True, default="MANUAL")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assessments = relationship("RiskAssessment", back_populates="risk", cascade="all, delete-orphan")
    treatments = relationship("RiskTreatment", back_populates="risk", cascade="all, delete-orphan")


class RiskAssessment(Base):
    """Re-assessments that update a risk's likelihood / impact over time."""
    __tablename__ = "risk_assessments"

    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk_register.risk_id", ondelete="CASCADE"), nullable=False, index=True)
    likelihood = Column(Integer, nullable=False)
    impact = Column(Integer, nullable=False)
    risk_score = Column(Integer, nullable=False)
    comments = Column(Text, nullable=True)
    assessed_at = Column(DateTime, default=datetime.utcnow)

    risk = relationship("RiskRegister", back_populates="assessments")


class RiskTreatment(Base):
    """Remediation / treatment plans linked to a risk."""
    __tablename__ = "risk_treatments"

    treatment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risk_register.risk_id", ondelete="CASCADE"), nullable=False, index=True)
    treatment_plan = Column(Text, nullable=False)
    status = Column(String(64), nullable=False, default="OPEN")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    risk = relationship("RiskRegister", back_populates="treatments")

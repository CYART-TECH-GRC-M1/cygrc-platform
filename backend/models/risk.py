import uuid
from datetime import datetime
import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, DateTime, Enum as SQLEnum, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.tenant import TenantStatus


class RiskTreatmentStatus(str, enum.Enum):
    OPEN = "OPEN"
    MITIGATED = "MITIGATED"
    CLOSED = "CLOSED"


class Risk(Base):
    __tablename__ = "risks"

    risk_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False, index=True)
    control_id = Column(UUID(as_uuid=True), ForeignKey("controls.control_id", ondelete="SET NULL"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    likelihood = Column(Integer, nullable=True)  # 1 to 5
    impact = Column(Integer, nullable=True)  # 1 to 5
    risk_score = Column(Integer, nullable=True)  # likelihood * impact (1 to 25)
    status = Column(
        SQLEnum(TenantStatus, name="tenant_status", create_type=False),
        default=TenantStatus.ACTIVE,
    )
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship("RiskAssessment", back_populates="risk", cascade="all, delete-orphan")
    treatments = relationship("RiskTreatment", back_populates="risk", cascade="all, delete-orphan")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risks.risk_id", ondelete="CASCADE"), nullable=False, index=True)
    assessor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    assessment_date = Column(Date, default=datetime.utcnow)
    likelihood = Column(Integer, nullable=False, default=3)
    impact = Column(Integer, nullable=False, default=3)
    risk_score = Column(Integer, nullable=False, default=9)
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    risk = relationship("Risk", back_populates="assessments")


class RiskTreatment(Base):
    __tablename__ = "risk_treatments"

    treatment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_id = Column(UUID(as_uuid=True), ForeignKey("risks.risk_id", ondelete="CASCADE"), nullable=False, index=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    treatment_plan = Column(Text, nullable=False)
    target_date = Column(Date, nullable=True)
    status = Column(
        SQLEnum(RiskTreatmentStatus, name="risk_status", create_type=False),
        default=RiskTreatmentStatus.OPEN,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    risk = relationship("Risk", back_populates="treatments")


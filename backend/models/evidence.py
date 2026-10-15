import enum
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.tenant import TenantStatus


class ReviewStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id", ondelete="CASCADE"), nullable=False)
    control_id = Column(UUID(as_uuid=True), ForeignKey("controls.control_id", ondelete="CASCADE"), nullable=False, index=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TenantStatus, name="tenant_status", create_type=False),
        default=TenantStatus.ACTIVE,
    )
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    files = relationship("EvidenceFile", back_populates="evidence", cascade="all, delete-orphan")
    reviews = relationship("EvidenceReview", back_populates="evidence", cascade="all, delete-orphan")


class EvidenceFile(Base):
    __tablename__ = "evidence_files"

    file_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.evidence_id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(BigInteger, nullable=True)
    file_type = Column(String(100), nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    evidence = relationship("Evidence", back_populates="files")


class EvidenceReview(Base):
    __tablename__ = "evidence_reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.evidence_id", ondelete="CASCADE"), nullable=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    review_status = Column(
        SQLEnum(ReviewStatus, name="review_status", create_type=False),
        default=ReviewStatus.PENDING,
    )
    comments = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, default=datetime.utcnow)

    evidence = relationship("Evidence", back_populates="reviews")

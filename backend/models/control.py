import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base
from backend.models.tenant import TenantStatus


class Framework(Base):
    __tablename__ = "frameworks"

    framework_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    controls = relationship("Control", back_populates="framework", cascade="all, delete-orphan")
    control_families = relationship("ControlFamily", back_populates="framework", cascade="all, delete-orphan")


class ControlFamily(Base):
    __tablename__ = "control_families"

    control_family_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.framework_id", ondelete="CASCADE"), nullable=False)
    family_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    framework = relationship("Framework", back_populates="control_families")
    controls = relationship("Control", back_populates="control_family")


class Control(Base):
    __tablename__ = "controls"

    control_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.framework_id", ondelete="CASCADE"), nullable=False)
    control_family_id = Column(UUID(as_uuid=True), ForeignKey("control_families.control_family_id", ondelete="SET NULL"), nullable=True)
    control_code = Column(String(50), nullable=False)
    control_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(
        SQLEnum(TenantStatus, name="tenant_status", create_type=False),
        default=TenantStatus.ACTIVE,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    framework = relationship("Framework", back_populates="controls")
    control_family = relationship("ControlFamily", back_populates="controls")
    tenant_mappings = relationship(
        "TenantControlMapping",
        back_populates="control",
        cascade="all, delete-orphan",
    )

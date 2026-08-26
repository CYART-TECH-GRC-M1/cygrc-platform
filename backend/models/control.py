from __future__ import annotations

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from backend.core.config import Base


class Framework(Base):
    __tablename__ = "frameworks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(80), nullable=False, default="compliance")
    is_default = Column(Boolean, nullable=False, default=True)

    controls = relationship("Control", back_populates="framework", cascade="all, delete-orphan")


class Control(Base):
    __tablename__ = "controls"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(120), nullable=False, index=True)
    framework_id = Column(Integer, ForeignKey("frameworks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="active")
    owner = Column(String(120), nullable=True)

    framework = relationship("Framework", back_populates="controls")
    tenant_controls = relationship("TenantControl", back_populates="control", cascade="all, delete-orphan")


class TenantControl(Base):
    __tablename__ = "tenant_controls"

    __table_args__ = (
        UniqueConstraint("tenant_id", "control_id", name="uq_tenant_control"),
    )

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(120), nullable=False, index=True)
    control_id = Column(Integer, ForeignKey("controls.id", ondelete="CASCADE"), nullable=False)

    control = relationship("Control", back_populates="tenant_controls")

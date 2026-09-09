import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


class Framework(Base):
    __tablename__ = "frameworks"

    framework_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_name = Column(String(255), unique=True, nullable=False, index=True)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    controls = relationship("Control", back_populates="framework", cascade="all, delete-orphan")


class Control(Base):
    __tablename__ = "controls"

    control_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.framework_id", ondelete="CASCADE"), nullable=False)
    control_family_id = Column(UUID(as_uuid=True), nullable=True)
    control_code = Column(String(50), nullable=False)
    control_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    framework = relationship("Framework", back_populates="controls")

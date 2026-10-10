import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False, default="SERVER")  # SERVER, WORKSTATION, CLOUD, NETWORK, WEB_APP
    ip_address = Column(String(45), nullable=True)
    hostname = Column(String(255), nullable=True)
    criticality = Column(String(50), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, DECOMMISSIONED
    tags = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.core.database import Base


class Asset(Base):
    __tablename__ = "assets"

    asset_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(100), nullable=False, default="SERVER")  # SERVER, WORKSTATION, CLOUD, NETWORK, WEB_APP, CONTAINER
    ip_address = Column(String(45), nullable=True, index=True)
    hostname = Column(String(255), nullable=True, index=True)
    criticality = Column(String(50), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, DECOMMISSIONED, RETIRED
    environment = Column(String(50), nullable=False, default="PROD")  # PROD, STAGING, DEV, TEST
    exposure = Column(String(50), nullable=False, default="INTERNAL")  # INTERNAL, EXTERNAL, DMZ, CLOUD
    owner = Column(String(255), nullable=True)
    mac_address = Column(String(50), nullable=True)
    os_name = Column(String(100), nullable=True)
    metadata_json = Column(JSON, nullable=True, default=dict)
    tags = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

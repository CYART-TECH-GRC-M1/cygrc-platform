import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, Integer
from backend.core.database import Base


class StixObject(Base):
    __tablename__ = "stix_objects"

    stix_id = Column(String(255), primary_key=True)
    tenant_id = Column(String, nullable=True, index=True)
    type = Column(String(100), nullable=False, index=True)  # indicator, malware, threat-actor, vulnerability
    spec_version = Column(String(20), nullable=False, default="2.1")
    name = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    pattern = Column(Text, nullable=True)
    labels = Column(JSON, nullable=True, default=list)
    confidence = Column(Integer, nullable=True, default=50)
    raw_stix = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

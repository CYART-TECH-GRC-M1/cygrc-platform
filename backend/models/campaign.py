import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text
from backend.core.database import Base


class RedTeamCampaign(Base):
    __tablename__ = "red_team_campaigns"

    campaign_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE")  # PLANNING, ACTIVE, COMPLETED
    techniques_tested = Column(JSON, nullable=True, default=list)  # list of MITRE technique IDs
    coverage_score = Column(String(20), nullable=True, default="0%")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

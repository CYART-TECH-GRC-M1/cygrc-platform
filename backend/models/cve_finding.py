from datetime import datetime
from sqlalchemy import Column, String, Float, Boolean, Text, DateTime
from backend.core.database import Base


class CVEFinding(Base):
    __tablename__ = "cve_findings"

    cve_id = Column(String(50), primary_key=True)  # e.g., "CVE-2026-1234"
    cvss_score = Column(Float, nullable=False, default=7.5)
    cvss_vector = Column(String(255), nullable=True)
    cisa_kev = Column(Boolean, nullable=False, default=False)  # Known Exploited Vulnerabilities flag
    summary = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    affected_product = Column(String(255), nullable=True)
    published_date = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

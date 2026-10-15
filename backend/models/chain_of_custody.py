import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text
from backend.core.database import Base


class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"

    custody_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=True, index=True)
    evidence_id = Column(String(255), nullable=False, index=True)
    item_description = Column(Text, nullable=False)
    custodian_name = Column(String(255), nullable=False)
    custodian_email = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False)  # COLLECTED, TRANSFERRED, ANALYZED, STORED, DISPOSED
    location = Column(String(255), nullable=True)
    hash_sha256 = Column(String(64), nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

import uuid
import enum
from datetime import datetime

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from backend.core.database import Base


class CustodyAction(str, enum.Enum):
    COLLECTED = "COLLECTED"
    TRANSFERRED = "TRANSFERRED"
    ACCESSED = "ACCESSED"
    ANALYZED = "ANALYZED"
    EXPORTED = "EXPORTED"


class DfirChainOfCustody(Base):
    __tablename__ = "dfir_chain_of_custody"

    custody_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
    )

    evidence_id = Column(
        UUID(as_uuid=True),
        ForeignKey("evidence.evidence_id", ondelete="CASCADE"),
        nullable=False,
    )

    performed_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    action = Column(
        SQLEnum(
            CustodyAction,
            name="dfir_custody_action",
            create_type=True,
        ),
        nullable=False,
    )

    source = Column(String(255), nullable=True)

    destination = Column(String(255), nullable=True)

    notes = Column(Text, nullable=True)

    integrity_hash = Column(String(128), nullable=True)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
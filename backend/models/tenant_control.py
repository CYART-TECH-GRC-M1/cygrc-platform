import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from backend.core.database import Base


class TenantControlMapping(Base):
    """Maps a shared catalog Control onto a Tenant. Controls stay global."""

    __tablename__ = "tenant_controls"
    __table_args__ = (
        UniqueConstraint("tenant_id", "control_id", name="uq_tenant_controls_tenant_id_control_id"),
        Index(
            "ix_tenant_controls_tenant_id_control_id",
            "tenant_id",
            "control_id",
            unique=True,
        ),
    )

    mapping_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
        nullable=False,
    )
    control_id = Column(
        UUID(as_uuid=True),
        ForeignKey("controls.control_id", ondelete="CASCADE"),
        nullable=False,
    )
    status = Column(String(50), default="ACTIVE", nullable=True)
    seeded_at = Column(DateTime, default=datetime.utcnow, nullable=True)

    tenant = relationship("Tenant", back_populates="control_mappings")
    control = relationship("Control", back_populates="tenant_mappings")

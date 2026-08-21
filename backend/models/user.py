import uuid
from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, Enum as SQLEnum, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from backend.core.database import Base

tenant_status_enum = SQLEnum(
    "ACTIVE", "INACTIVE", "SUSPENDED",
    name="tenant_status",
    create_type=False,  # type already exists in DB via schema.sql
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.tenant_id"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    keycloak_id = Column(String(255), nullable=True)
    status = Column(tenant_status_enum, server_default="ACTIVE")
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

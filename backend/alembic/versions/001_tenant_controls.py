"""Add tenant_controls mapping table with unique (tenant_id, control_id) index.

Revision ID: 001_tenant_controls
Revises:
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001_tenant_controls"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tenant_controls and unique composite index (tenant_id, control_id)."""
    op.create_table(
        "tenant_controls",
        sa.Column("mapping_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("control_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("seeded_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.tenant_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["control_id"],
            ["controls.control_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("mapping_id"),
        sa.UniqueConstraint(
            "tenant_id",
            "control_id",
            name="uq_tenant_controls_tenant_id_control_id",
        ),
    )
    op.create_index(
        "ix_tenant_controls_tenant_id_control_id",
        "tenant_controls",
        ["tenant_id", "control_id"],
        unique=True,
    )


def downgrade() -> None:
    """Drop tenant_controls (unique index is removed with the table)."""
    op.drop_index("ix_tenant_controls_tenant_id_control_id", table_name="tenant_controls")
    op.drop_table("tenant_controls")

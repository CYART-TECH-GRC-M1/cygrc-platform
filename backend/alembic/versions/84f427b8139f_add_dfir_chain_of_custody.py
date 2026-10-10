
"""add DFIR chain of custody

Revision ID: 84f427b8139f
Revises: df9270459e8d
Create Date: 2026-10-08
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "84f427b8139f"
down_revision: Union[str, Sequence[str], None] = "df9270459e8d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the DFIR chain of custody table."""

    bind = op.get_bind()

    custody_action = postgresql.ENUM(
        "COLLECTED",
        "TRANSFERRED",
        "ACCESSED",
        "ANALYZED",
        "EXPORTED",
        name="dfir_custody_action",
        create_type=False,
    )

    # Create the PostgreSQL enum only if it is missing.
    custody_action.create(bind, checkfirst=True)

    op.create_table(
        "dfir_chain_of_custody",
        sa.Column(
            "custody_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "performed_by",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("action", custody_action, nullable=False),
        sa.Column("source", sa.String(255), nullable=True),
        sa.Column("destination", sa.String(255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("integrity_hash", sa.String(128), nullable=True),
        sa.Column(
            "timestamp",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.tenant_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["evidence_id"],
            ["evidence.evidence_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["performed_by"],
            ["users.user_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("custody_id"),
    )


def downgrade() -> None:
    """Remove the DFIR chain of custody table and its enum."""

    bind = op.get_bind()

    op.drop_table("dfir_chain_of_custody")

    custody_action = postgresql.ENUM(
        "COLLECTED",
        "TRANSFERRED",
        "ACCESSED",
        "ANALYZED",
        "EXPORTED",
        name="dfir_custody_action",
        create_type=False,
    )

    custody_action.drop(bind, checkfirst=True)

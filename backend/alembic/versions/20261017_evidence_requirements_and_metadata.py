"""Add evidence requirements and upload metadata.

Revision ID: 20261017_evidence
Revises:
Create Date: 2026-10-17
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20261017_evidence"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence_requirements",
        sa.Column(
            "requirement_id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.tenant_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "control_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("controls.control_id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "source_type",
            sa.String(length=50),
            server_default="MANUAL",
        ),
        sa.Column(
            "max_age_days",
            sa.Integer(),
            server_default="90",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
        ),
    )

    op.add_column(
        "evidence",
        sa.Column("requirement_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "evidence",
        sa.Column("blob_s3_key", sa.Text(), nullable=True),
    )
    op.add_column(
        "evidence",
        sa.Column("sha256", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "evidence",
        sa.Column("file_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "evidence",
        sa.Column("file_size", sa.BigInteger(), nullable=True),
    )
    op.add_column(
        "evidence",
        sa.Column("content_type", sa.String(length=100), nullable=True),
    )

    op.create_foreign_key(
        "fk_evidence_requirement",
        "evidence",
        "evidence_requirements",
        ["requirement_id"],
        ["requirement_id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_evidence_requirement",
        "evidence",
        type_="foreignkey",
    )

    op.drop_column("evidence", "content_type")
    op.drop_column("evidence", "file_size")
    op.drop_column("evidence", "file_name")
    op.drop_column("evidence", "sha256")
    op.drop_column("evidence", "blob_s3_key")
    op.drop_column("evidence", "requirement_id")

    op.drop_table("evidence_requirements")

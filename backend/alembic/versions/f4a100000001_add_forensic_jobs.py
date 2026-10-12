"""Add durable forensic job records."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f4a100000001"
down_revision: Union[str, Sequence[str], None] = "d6c0f522ff09"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forensic_jobs",
        sa.Column("job_id", sa.String(length=36), primary_key=True),
        sa.Column("tenant_id", sa.String(length=36), nullable=False),
        sa.Column("actor_id", sa.String(length=36), nullable=False),
        sa.Column("case_id", sa.String(length=100), nullable=True),
        sa.Column("target", sa.String(length=500), nullable=False),
        sa.Column("tool", sa.String(length=50), nullable=False),
        sa.Column("operation", sa.String(length=50), nullable=False),
        sa.Column("artifact_name", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("external_job_id", sa.String(length=255), nullable=True),
        sa.Column("parameters", sa.JSON(), nullable=True),
        sa.Column("result_metadata", sa.JSON(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "cancellation_requested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_forensic_jobs_tenant_id", "forensic_jobs", ["tenant_id"])
    op.create_index("ix_forensic_jobs_actor_id", "forensic_jobs", ["actor_id"])
    op.create_index("ix_forensic_jobs_case_id", "forensic_jobs", ["case_id"])
    op.create_index("ix_forensic_jobs_status", "forensic_jobs", ["status"])
    op.create_index(
        "ix_forensic_jobs_external_job_id",
        "forensic_jobs",
        ["external_job_id"],
    )
    op.create_index(
        "ix_forensic_jobs_tenant_status",
        "forensic_jobs",
        ["tenant_id", "status"],
    )


def downgrade() -> None:
    op.drop_index("ix_forensic_jobs_tenant_status", table_name="forensic_jobs")
    op.drop_index("ix_forensic_jobs_external_job_id", table_name="forensic_jobs")
    op.drop_index("ix_forensic_jobs_status", table_name="forensic_jobs")
    op.drop_index("ix_forensic_jobs_case_id", table_name="forensic_jobs")
    op.drop_index("ix_forensic_jobs_actor_id", table_name="forensic_jobs")
    op.drop_index("ix_forensic_jobs_tenant_id", table_name="forensic_jobs")
    op.drop_table("forensic_jobs")

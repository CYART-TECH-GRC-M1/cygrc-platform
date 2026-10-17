"""Add tenant control mappings and evidence pipeline metadata."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20261017_evidence_safe"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    tables = set(inspector.get_table_names())

    # Tenant-to-control mappings used by the application.
    if "tenant_controls" not in tables:
        op.create_table(
            "tenant_controls",
            sa.Column(
                "mapping_id",
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
            sa.Column("status", sa.String(50), nullable=True),
            sa.Column("seeded_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint(
                "tenant_id",
                "control_id",
                name="uq_tenant_controls_tenant_id_control_id",
            ),
        )

    inspector = sa.inspect(bind)
    indexes = {
        index["name"]
        for index in inspector.get_indexes("tenant_controls")
    } if "tenant_controls" in sa.inspect(bind).get_table_names() else set()

    if "tenant_controls" in sa.inspect(bind).get_table_names():
        if "ix_tenant_controls_tenant_id_control_id" not in indexes:
            op.create_index(
                "ix_tenant_controls_tenant_id_control_id",
                "tenant_controls",
                ["tenant_id", "control_id"],
                unique=True,
            )

    # Evidence requirements.
    if "evidence_requirements" not in tables:
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
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column(
                "source_type",
                sa.String(50),
                nullable=True,
                server_default="MANUAL",
            ),
            sa.Column(
                "max_age_days",
                sa.Integer(),
                nullable=True,
                server_default="90",
            ),
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=True,
                server_default=sa.func.now(),
            ),
        )

    # Add only columns missing from the existing evidence table.
    existing_columns = {
        column["name"]
        for column in sa.inspect(bind).get_columns("evidence")
    }

    additions = [
        ("requirement_id", postgresql.UUID(as_uuid=True)),
        ("blob_s3_key", sa.Text()),
        ("sha256", sa.String(64)),
        ("file_name", sa.String(255)),
        ("file_size", sa.BigInteger()),
        ("content_type", sa.String(100)),
    ]

    for column_name, column_type in additions:
        if column_name not in existing_columns:
            op.add_column(
                "evidence",
                sa.Column(column_name, column_type, nullable=True),
            )

    # Add the foreign key only if it does not already exist.
    foreign_keys = {
        fk["name"]
        for fk in sa.inspect(bind).get_foreign_keys("evidence")
    }

    if "fk_evidence_requirement" not in foreign_keys:
        op.create_foreign_key(
            "fk_evidence_requirement",
            "evidence",
            "evidence_requirements",
            ["requirement_id"],
            ["requirement_id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    raise RuntimeError(
        "This compatibility migration is intentionally irreversible. "
        "Restore from a verified backup if rollback is required."
    )

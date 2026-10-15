"""add tenant isolation to DFIR custody

Revision ID: cd2056c16004
Revises: 84f427b8139f
"""

from typing import Sequence, Union

from alembic import op

revision: str = "cd2056c16004"
down_revision: Union[str, Sequence[str], None] = "84f427b8139f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Enable tenant isolation on DFIR chain-of-custody records."""
    op.execute("""
        ALTER TABLE dfir_chain_of_custody ENABLE ROW LEVEL SECURITY;
        ALTER TABLE dfir_chain_of_custody FORCE ROW LEVEL SECURITY;

        CREATE POLICY tenant_isolation_dfir_custody
        ON dfir_chain_of_custody
        USING (
            tenant_id = current_setting('app.current_tenant')::uuid
        )
        WITH CHECK (
            tenant_id = current_setting('app.current_tenant')::uuid
        );
    """)


def downgrade() -> None:
    """Remove the DFIR tenant-isolation policy."""
    op.execute("""
        DROP POLICY IF EXISTS tenant_isolation_dfir_custody
        ON dfir_chain_of_custody;

        ALTER TABLE dfir_chain_of_custody NO FORCE ROW LEVEL SECURITY;
        ALTER TABLE dfir_chain_of_custody DISABLE ROW LEVEL SECURITY;
    """)

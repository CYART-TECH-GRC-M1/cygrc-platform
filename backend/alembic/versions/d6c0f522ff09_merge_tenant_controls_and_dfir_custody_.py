"""merge_tenant_controls_and_dfir_custody_heads

Revision ID: d6c0f522ff09
Revises: 001_tenant_controls, cd2056c16004
Create Date: 2026-10-11 13:58:04.603529

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6c0f522ff09'
down_revision: Union[str, Sequence[str], None] = ('001_tenant_controls', 'cd2056c16004')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass

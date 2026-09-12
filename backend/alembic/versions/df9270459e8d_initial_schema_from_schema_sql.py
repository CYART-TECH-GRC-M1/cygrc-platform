"""initial schema from schema.sql

Revision ID: df9270459e8d
Revises: 
Create Date: 2026-08-07 11:55:44.056672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pathlib import Path


# revision identifiers, used by Alembic.
revision: str = 'df9270459e8d'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    schema_file = Path(__file__).resolve().parents[3] / "database" / "migrations" / "schema.sql"
    sql = schema_file.read_text(encoding="utf-8")
    op.execute(sql)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
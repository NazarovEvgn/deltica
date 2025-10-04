"""Initial migration: create equipment, verification, responsibility, finance tables

Revision ID: f6eeca7cc210
Revises: 
Create Date: 2025-09-27 19:02:41.301962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6eeca7cc210'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Note: Tables already exist in database, this migration marks them as managed by Alembic
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Note: This would drop all tables, but we'll keep them for safety
    pass

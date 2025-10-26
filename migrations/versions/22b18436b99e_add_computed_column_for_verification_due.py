"""Add computed column for verification_due

Revision ID: 22b18436b99e
Revises: f6eeca7cc210
Create Date: 2025-10-11 10:03:33.671339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22b18436b99e'
down_revision: Union[str, Sequence[str], None] = 'f6eeca7cc210'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert verification_due to computed column."""
    # Drop the existing column if it exists
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_name='verification' AND column_name='verification_due'
            ) THEN
                ALTER TABLE verification DROP COLUMN verification_due;
            END IF;
        END $$;
    """)

    # Add computed column
    op.execute("""
        ALTER TABLE verification
        ADD COLUMN verification_due DATE
        GENERATED ALWAYS AS (
            (verification_date + make_interval(months => verification_interval) - interval '1 day')::date
        ) STORED
    """)


def downgrade() -> None:
    """Revert verification_due to regular column."""
    # Drop computed column
    op.drop_column('verification', 'verification_due')

    # Add regular column back
    op.add_column('verification', sa.Column('verification_due', sa.Date(), nullable=False))

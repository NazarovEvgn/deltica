"""Add computed column for status

Revision ID: 9c0f57b4f3b7
Revises: 22b18436b99e
Create Date: 2025-10-11 11:00:25.534635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9c0f57b4f3b7'
down_revision: Union[str, Sequence[str], None] = '22b18436b99e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add trigger for automatic status calculation."""
    # Create function to calculate status
    op.execute("""
        CREATE OR REPLACE FUNCTION update_verification_status()
        RETURNS TRIGGER AS $$
        DECLARE
            v_verification_due DATE;
            v_days_until_due INTEGER;
            v_new_status VARCHAR;
        BEGIN
            -- Calculate verification_due
            v_verification_due := (NEW.verification_date + make_interval(months => NEW.verification_interval) - interval '1 day')::date;
            v_days_until_due := v_verification_due - CURRENT_DATE;

            -- Calculate status based on conditions
            IF CURRENT_DATE > v_verification_due THEN
                v_new_status := 'status_expired';
            ELSIF v_days_until_due <= 14 THEN
                v_new_status := 'status_expiring';
            ELSIF NEW.verification_state = 'state_work' THEN
                v_new_status := 'status_fit';
            ELSIF NEW.verification_state = 'state_storage' THEN
                v_new_status := 'status_storage';
            ELSIF NEW.verification_state = 'state_verification' THEN
                v_new_status := 'status_verification';
            ELSIF NEW.verification_state = 'state_repair' THEN
                v_new_status := 'status_repair';
            ELSIF NEW.verification_state = 'state_archived' THEN
                v_new_status := 'status_fit';
            ELSE
                v_new_status := 'status_fit';
            END IF;

            NEW.status := v_new_status;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
        CREATE TRIGGER trigger_update_verification_status
        BEFORE INSERT OR UPDATE ON verification
        FOR EACH ROW
        EXECUTE FUNCTION update_verification_status();
    """)


def downgrade() -> None:
    """Remove trigger for automatic status calculation."""
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS trigger_update_verification_status ON verification")

    # Drop function
    op.execute("DROP FUNCTION IF EXISTS update_verification_status()")

"""drop unique key constraint

Revision ID: 7785d9d74786
Revises: 7b6b049317c9
Create Date: 2022-02-23 12:13:43.358290
Revision by: Luci Pak

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "7785d9d74786"
down_revision = "7b6b049317c9"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_index("instrument_serial_number", "mantarray_recording_sessions")


def downgrade():
    op.create_unique_constraint(
        "instrument_serial_number",
        "mantarray_recording_sessions",
        ["instrument_serial_number", "recording_started_at"],
    )

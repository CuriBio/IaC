"""Alter table columns to microseconds

Revision ID: f13d3833f05c
Revises: 10c965144f38
Create Date: 2021-12-29 11:59:35.616725
Revision  by: Luci Pak

"""
from alembic import op
import sqlalchemy as sa  # noqa

# revision identifiers, used by Alembic.
revision = "f13d3833f05c"
down_revision = "10c965144f38"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "mantarray_recording_sessions",
        "length_centimilliseconds",
        new_column_name="length_microseconds",
        existing_type=sa.INTEGER(),
    )
    op.alter_column(
        "mantarray_raw_files",
        "length_centimilliseconds",
        new_column_name="length_microseconds",
        existing_type=sa.INTEGER(),
    )


def downgrade():
    op.alter_column(
        "mantarray_recording_sessions",
        "length_microseconds",
        new_column_name="length_centimilliseconds",
        existing_type=sa.INTEGER(),
    )
    op.alter_column(
        "mantarray_raw_files",
        "length_microseconds",
        new_column_name="length_centimilliseconds",
        existing_type=sa.INTEGER(),
    )

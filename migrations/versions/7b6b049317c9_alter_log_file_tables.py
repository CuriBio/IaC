"""alter log file tables

Revision ID: 7b6b049317c9
Revises: f13d3833f05c
Create Date: 2022-01-10 10:52:02.733438
Revision by: Luci Pak

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7b6b049317c9"
down_revision = "f13d3833f05c"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("mantarray_frontend_log_files")
    op.drop_constraint(
        "mantarray_recording_sessions_ibfk_2", "mantarray_recording_sessions", type_="foreignkey"
    )
    op.drop_index("backend_log_id", "mantarray_recording_sessions")
    op.alter_column(
        "mantarray_recording_sessions",
        "backend_log_id",
        new_column_name="session_log_id",
        existing_type=sa.VARCHAR(255),
    )
    op.drop_table("mantarray_backend_log_files")
    op.create_table(
        "mantarray_session_log_files",
        sa.Column("session_log_id", sa.VARCHAR(255), primary_key=True),
        sa.Column("upload_id", sa.INTEGER()),
        sa.Column("bucket", sa.VARCHAR(255)),
        sa.Column("object_key", sa.VARCHAR(255)),
        sa.Column("software_version", sa.VARCHAR(255)),
        sa.Column("file_format_version", sa.VARCHAR(255)),
        sa.Column("customer_account_id", sa.VARCHAR(255)),
        sa.Column("user_account_id", sa.VARCHAR(255)),
        sa.ForeignKeyConstraint(["upload_id"], ["uploaded_s3_objects.id"],),
    )
    op.create_foreign_key(
        "mantarray_recording_sessions_ibfk_2",
        "mantarray_recording_sessions",
        "mantarray_session_log_files",
        ["session_log_id"],
        ["session_log_id"],
    )


def downgrade():
    op.drop_table("mantarray_session_log_files")
    op.drop_constraint(
        "mantarray_recording_sessions_ibfk_2", "mantarray_recording_sessions", type_="foreignkey"
    )
    op.excute("ALTER TABLE mantarray_recording_sessions DROP KEY session_log_id;")
    op.alter_column(
        "mantarray_recording_sessions",
        "session_log_id",
        new_column_name="backend_log_id",
        existing_type=sa.VARCHAR(255),
    )
    op.create_table(
        "mantarray_backend_log_files",
        sa.Column("backend_log_id", sa.VARCHAR(255), primary_key=True),
        sa.Column("upload_id", sa.VARCHAR(255)),
        sa.Column("frontend_log_id", sa.VARCHAR(255)),
        sa.Column("exit_code", sa.TINYINT()),
        sa.Column("software_version", sa.VARCHAR(255)),
        sa.Column("file_format_version", sa.VARCHAR(255)),
        sa.Column("started_at", sa.DateTime()),
        sa.Column("ended_at", sa.DateTime()),
        sa.Column("last_used_customer_account_id", sa.VARCHAR(255)),
        sa.Column("last_used_user_account_id", sa.VARCHAR(255)),
        sa.ForeignKeyConstraint(["upload_id"], ["uploaded_s3_objects.id"],),
    )
    op.create_table(
        "mantarray_frontend_log_files",
        sa.Column("frontend_log_id", sa.VARCHAR(255), primary_key=True),
        sa.Column("upload_id", sa.VARCHAR(255)),
        sa.ForeignKeyConstraint(["upload_id"], ["uploaded_s3_objects.id"],),
    )
    op.create_foreign_key(
        "mantarray_recording_sessions_ibfk_2",
        "mantarray_recording_sessions",
        "mantarray_backend_log_files",
        ["backend_log_id"],
        ["backend_log_id"],
    )

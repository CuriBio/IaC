from io import StringIO
import logging
from logging.config import fileConfig
import os

from alembic import context
import paramiko
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sshtunnel import SSHTunnelForwarder

# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic")

# ssh config
pkey = StringIO(os.environ.get("KEY"))
P_KEY = paramiko.RSAKey.from_private_key(pkey)

ssh_user_host = os.environ.get("EC2_HOST").split("@")
SSH_USER = ssh_user_host[0]
SSH_HOST = ssh_user_host[1]
SSH_PORT = 22

# mysql config
DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USERNAME")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_NAME = "mantarray_recordings"
DB_PORT = 3306

LOCAL_HOST = "127.0.0.1"

with SSHTunnelForwarder(
    (SSH_HOST, SSH_PORT), ssh_username=SSH_USER, ssh_pkey=P_KEY, remote_bind_address=(DB_HOST, DB_PORT)
) as tunnel:
    db_url = (
        "mysql://"
        + DB_USER
        + ":"
        + DB_PASSWORD
        + "@"
        + LOCAL_HOST
        + ":"
        + str(tunnel.local_bind_port)
        + "/"
        + DB_NAME
    )
    engine = create_engine(db_url)

    metadata = MetaData()
    with engine.connect() as conn:
        uploaded_s3_objects = Table("uploaded_s3_objects", metadata, autoload_with=conn)
        sbs_labware_barcodes = Table("sbs_labware_barcodes", metadata, autoload_with=conn)
        s3_objects = Table("s3_objects", metadata, autoload_with=conn)
        mantarray_recording_sessions = Table("mantarray_recording_sessions", metadata, autoload_with=conn)
        mantarray_raw_files = Table("mantarray_raw_files", metadata, autoload_with=conn)
        mantarray_frontend_log_files = Table("mantarray_frontend_log_files", metadata, autoload_with=conn)
        mantarray_backend_log_files = Table("mantarray_backend_log_files", metadata, autoload_with=conn)
        labware_definitions = Table("labware_definitions", metadata, autoload_with=conn)
        experiment_labware = Table("experiment_labware", metadata, autoload_with=conn)
        barcoded_sbs_labware = Table("barcoded_sbs_labware", metadata, autoload_with=conn)

    target_metadata = metadata

    def run_migrations_offline():
        """Run migrations in 'offline' mode.

        This configures the context with just a URL
        and not an Engine, though an Engine is acceptable
        here as well.  By skipping the Engine creation
        we don't even need a DBAPI to be available.

        Calls to context.execute() here emit the given string to the
        script output.

        """
        context.configure(
            url=db_url,
            target_metadata=target_metadata,
            literal_binds=True,
            dialect_opts={"paramstyle": "named"},
        )

        with context.begin_transaction():
            context.run_migrations()

    def run_migrations_online():
        """Run migrations in 'online' mode.

        In this scenario we need to create an Engine
        and associate a connection with the context.

        """
        with engine.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata, version_table="alembic_version",
            )

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

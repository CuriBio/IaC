from logging.config import fileConfig
import os
from io import StringIO
from alembic import context
import paramiko
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sshtunnel import SSHTunnelForwarder

# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

# ssh config
pkey = StringIO(os.environ.get("KEY"))
mypkey = paramiko.RSAKey.from_private_key(pkey)
ssh_host = os.environ.get("EC2_HOST")
ssh_user = "ec2-user"
ssh_port = 22

# mysql config
sql_hostname = os.environ.get("DB_HOST")
sql_username = os.environ.get("DB_USER")
sql_password = os.environ.get("DB_PASSWORD")
sql_main_database = "mantarray_recordings"
sql_port = 3306
host = "127.0.0.1"

# access to the values within the .ini file in use.
config = context.config
fileConfig(config.config_file_name)

with SSHTunnelForwarder(
    (ssh_host, ssh_port), ssh_username=ssh_user, ssh_pkey=mypkey, remote_bind_address=(sql_hostname, sql_port)
) as tunnel:

    metadata = MetaData()
    db_url = (
        "mysql://"
        + sql_username
        + ":"
        + sql_password
        + "@"
        + host
        + ":"
        + str(tunnel.local_bind_port)
        + "/"
        + sql_main_database
    )
    engine = create_engine(db_url)
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
                connection=connection,
                target_metadata=target_metadata,
                version_table="alembic_version_%s" % config.config_ini_section,
            )

            with context.begin_transaction():
                context.run_migrations()

    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()

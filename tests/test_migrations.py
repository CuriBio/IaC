import os

from alembic.config import Config
from alembic.script import ScriptDirectory

# import paramiko
# from sshtunnel import SSHTunnelForwarder
# import pytest
# import sshtunnel
# import sqlalchemy

INI_PATH = os.path.join(os.path.dirname(os.path.abspath("IaC")), "alembic.ini")
ALEMBIC_CONF = Config(INI_PATH)


def test_migrations__only_single_head_revision_in_migrations():
    # config.set_main_option("script_location", "/migrations")
    script_dir = ScriptDirectory.from_config(ALEMBIC_CONF)
    # This will raise if there are multiple heads
    script_dir.get_current_head()


# def get_revisions():
#     # Get directory object with Alembic migrations
#     revisions_dir = ScriptDirectory.from_config(ALEMBIC_CONF)

#     # Get & sort migrations, from first to last
#     revisions = list(revisions_dir.walk_revisions())
#     revisions.reverse()

#     return revisions


# @pytest.mark.parametrize("revision", get_revisions())
# def test_migrations_stairway(revision, mocker):
#     mocker.patch.object(paramiko.RSAKey, "from_private_key")
#     mocked_tunnel = mocker.patch.object(sshtunnel, "SSHTunnelForwarder")
#     mocker.patch.object(os.environ, "get", return_value="test@test")
#     mocker.patch.object(sqlalchemy, "create_engine")
#     mocked_tunnel.start()
#     upgrade(ALEMBIC_CONF, revision.revision)

#     # We need -1 for downgrading first migration (its down_revision is None)
#     downgrade(ALEMBIC_CONF, revision.down_revision or "-1")
#     upgrade(ALEMBIC_CONF, revision.revision)


# # def test_migrations__errors_when_ssh_tunnel_fails():

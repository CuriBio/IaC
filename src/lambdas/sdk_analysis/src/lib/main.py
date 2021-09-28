from io import StringIO
import logging

import paramiko
import pymysql
from sshtunnel import SSHTunnelForwarder

from .aws_utils import get_remote_aws_endpoints
from .aws_utils import get_s3_object_contents
from .aws_utils import get_ssm_secrets
from .helpers import load_data_to_dataframe

INFO_DICT = {}

# set logger
logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger()

# Queries
insert_into_uploaded_s3_table = """
    INSERT INTO uploaded_s3_objects(bucket, object_key, upload_started_at, uploading_computer_name)
    VALUES (%s, %s, NOW(), %s);
    """

insert_into_mantarray_recording_sessions = """
    INSERT INTO mantarray_recording_sessions(mantarray_recording_session_id, instrument_serial_number, backend_log_id, acquisition_started_at, length_centimilliseconds,
    recording_started_at)
    VALUES (%s, %s, %s, %s, %s, %s);
    """

insert_into_mantarray_raw_files = """
    INSERT INTO mantarray_raw_files(bucket_id, well_index, length_centimilliseconds, recording_started_at, mantarray_recording_session_id)
    VALUES (SELECT id FROM uploaded_s3_objects ORDER BY id DESC LIMIT 1, %s, %s, %s, %s);
    """

insert_into_s3_objects = """
    INSERT INTO s3_objects(bucket_id, kilobytes, stored_at) VALUES (SELECT id FROM uploaded_s3_objects ORDER BY id DESC LIMIT 1, %s, %s);
    """


def handle_db_metadata_insertions(bucket: str, key: str, file, r):
    """ Open an SSH tunnel and connect using a username and password. Query database.
        Args:
            file: .xlsx file containing aggregated metadata for recording
            r: PlateRecording instance for individual well data
    """

    if not INFO_DICT:
        set_info_dict()

    with SSHTunnelForwarder(
        (INFO_DICT["ssh_host"], 22),
        ssh_username=INFO_DICT["ssh_user"],
        ssh_pkey=INFO_DICT["k"],
        remote_bind_address=(INFO_DICT["db_host"], 3306),
    ) as tunnel:
        # should this be a different host once deployed?
        try:
            conn = pymysql.connect(
                host=INFO_DICT["db_localhost"],
                user=INFO_DICT["db_username"],
                passwd=INFO_DICT["db_password"],
                db=INFO_DICT["db_name"],
                port=tunnel.local_bind_port,
            )
            logger.info("Successful ssh connection to Aurora database")
        except Exception as e:
            logger.error(f"Failed connection to Aurora database: {e}")

        cur = conn.cursor()

        formatted_data = load_data_to_dataframe(file, r)
        metadata = formatted_data["metadata"]
        well_data = formatted_data["well_data"]
        s3_size = get_s3_object_contents(bucket, key)

        try:
            uploaded_s3_tuple = (bucket, key, metadata["uploading_computer_name"])
            cur.execute(insert_into_uploaded_s3_table, uploaded_s3_tuple)

            recording_session_tuple = (
                metadata["mantarray_recording_session_id"],
                metadata["instrument_serial_number"],
                metadata["backend_log_id"],
                metadata["acquisition_started_at"],
                metadata["length_centimilliseconds"],
                metadata["recording_started_at"],
            )
            cur.execute(insert_into_mantarray_recording_sessions, recording_session_tuple)

            s3_object_tuple = (s3_size, metadata["file_creation_timestamp"])
            cur.execute(insert_into_s3_objects, s3_object_tuple)
        except Exception as e:
            logger.error(f"Error inserting meta data into database: {e}")

        try:
            for well in well_data:
                well_tuple = (
                    well["well_index"],
                    well["length_centimilliseconds"],
                    well["recording_started_at"],
                    metadata["mantarray_recording_session_id"],
                )
                cur.execute(insert_into_mantarray_raw_files, well_tuple)
        except Exception as e:
            logger.error(f"Error inserting individual well data into database: {e}")

        tunnel.close()
    return


def set_info_dict():
    # Retrieve DB creds
    secrets = get_ssm_secrets()
    INFO_DICT["db_username"] = secrets["username"]
    INFO_DICT["db_password"] = secrets["password"]

    # Change private key into correct format
    ssh_pkey = secrets["ssh_pkey"]
    pkey = StringIO(ssh_pkey)
    INFO_DICT["k"] = paramiko.RSAKey.from_private_key(pkey)

    # Retrieve db and ec2 IP addesses to SSH
    endpoints = get_remote_aws_endpoints()
    INFO_DICT["db_host"] = endpoints["rds_endpoint"]
    INFO_DICT["ssh_host"] = endpoints["ec2_endpoint"]
    INFO_DICT["ssh_user"] = "ec2-user"
    INFO_DICT["db_name"] = "mantarray_recordings"

    # set local IP
    INFO_DICT["db_localhost"] = "127.0.0.1"

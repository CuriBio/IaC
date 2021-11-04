# from io import StringIO
import logging
import sys

import pymysql

from .aws_utils import get_remote_aws_host
from .aws_utils import get_s3_object_contents
from .aws_utils import get_ssm_secrets
from .helpers import load_data_to_dataframe

# remove AWS pre-config that interferes with custom config
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

# set up custom basic config
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO, stream=sys.stdout
)
logger = logging.getLogger(__name__)

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
    INSERT INTO mantarray_raw_files(well_index, object_id, length_centimilliseconds, recording_started_at, mantarray_recording_session_id)
    VALUES (%s, %s, %s, %s, %s);
    """

insert_into_s3_objects = """
    INSERT INTO s3_objects(object_id, kilobytes, stored_at, md5) VALUES (%s, %s, %s, %s);
    """

select_last_object_id = """SELECT id FROM uploaded_s3_objects ORDER BY id DESC LIMIT 1"""

INFO_DICT = {}


def handle_db_metadata_insertions(bucket: str, key: str, args: list):
    """
        args:
            contains <file>.xlsx, individual well data, and the md5 hash
    """

    if not INFO_DICT:
        set_info_dict()

    try:
        conn = pymysql.connect(
            host=INFO_DICT["db_host"],
            user=INFO_DICT["db_username"],
            passwd=INFO_DICT["db_password"],
            db=INFO_DICT["db_name"],
        )
        logger.info("Successful connection to Aurora database")
    except Exception as e:
        raise Exception(f"Failed connection to Aurora database: {e}")

    formatted_data = load_data_to_dataframe(args[0], args[1])
    metadata = formatted_data["metadata"]
    well_data = formatted_data["well_data"]
    s3_size = get_s3_object_contents(bucket, key)

    cur = conn.cursor()

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

        s3_object_tuple = (select_last_object_id, s3_size, metadata["file_creation_timestamp"], args[2])
        cur.execute(insert_into_s3_objects, s3_object_tuple)

        logger.info("Executing queries to the database in relation to aggregated metadata")
    except Exception as e:
        raise Exception(f"Error inserting meta data into database: {e}")

    try:
        for well in well_data:
            well_tuple = (
                well["well_index"],
                select_last_object_id,
                well["length_centimilliseconds"],
                well["recording_started_at"],
                metadata["mantarray_recording_session_id"],
            )
            cur.execute(insert_into_mantarray_raw_files, well_tuple)

        logger.info("Executing queries to the database in relation individual well data")
    except Exception as e:
        raise Exception(f"Error inserting individual well data into database: {e}")

    conn.commit()


def set_info_dict():
    # Retrieve DB creds
    secrets = get_ssm_secrets()
    INFO_DICT["db_username"] = secrets["username"]
    INFO_DICT["db_password"] = secrets["password"]

    # Retrieve db and ec2 IP addesses to SSH
    rds_host = get_remote_aws_host()
    INFO_DICT["db_host"] = rds_host
    INFO_DICT["db_name"] = "mantarray_recordings"

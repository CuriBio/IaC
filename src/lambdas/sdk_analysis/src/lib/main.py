# from io import StringIO
import logging
import os
import sys

import pymysql

from .aws_utils import get_s3_object_contents
from .aws_utils import get_ssm_secrets
from .helpers import load_data_to_dataframe
from .queries import INSERT_INT0_UPLOADED_S3_OBJECTS
from .queries import INSERT_INTO_MANTARRAY_RAW_FILES
from .queries import INSERT_INTO_MANTARRAY_RECORDING_SESSIONS
from .queries import INSERT_INTO_MANTARRAY_SESSION_LOG_FILES
from .queries import INSERT_INTO_S3_OBJECTS

SDK_ANALYZED_BUCKET = os.environ.get("SDK_ANALYZED_BUCKET")
LOGS_BUCKET = os.environ.get("LOGS_BUCKET")
DB_CLUSTER_ENDPOINT = os.environ.get("DB_CLUSTER_ENDPOINT")

# set up custom basic config
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO, stream=sys.stdout
)
logger = logging.getLogger(__name__)

INFO_DICT = {}


def handle_db_metadata_insertions(args: list):
    """
    args:
        contains <file>.xlsx, individual well data, and the md5 hash
    """

    if not INFO_DICT:
        set_info_dict(args)

    try:
        conn = pymysql.connect(
            host=DB_CLUSTER_ENDPOINT,
            user=INFO_DICT["db_username"],
            passwd=INFO_DICT["db_password"],
            db=INFO_DICT["db_name"],
        )
        logger.info("Successful connection to Aurora database")
    except Exception as e:
        raise Exception(f"failed db connection: {e}")

    metadata, well_data = load_data_to_dataframe(INFO_DICT["sdk_xlsx"], INFO_DICT["pr"])
    s3_size = get_s3_object_contents(SDK_ANALYZED_BUCKET, INFO_DICT["sdk_analysis_key"])
    customer_account_id = INFO_DICT["sdk_analysis_key"].split("/")[0]
    user_account_id = INFO_DICT["sdk_analysis_key"].split("/")[1]

    cur = conn.cursor()

    logger.info("Executing queries to the database in relation to aggregated metadata")
    try:
        uploaded_sdk_tuple = (
            SDK_ANALYZED_BUCKET,
            INFO_DICT["sdk_analysis_key"],
            metadata["uploading_computer_name"],
        )
        cur.execute(INSERT_INT0_UPLOADED_S3_OBJECTS, uploaded_sdk_tuple)
    except Exception as e:
        raise Exception(f"in uploaded_s3_objects: {e}")

    try:
        recording_session_tuple = (
            metadata["mantarray_recording_session_id"],
            customer_account_id,
            user_account_id,
            metadata["instrument_serial_number"],
            metadata["session_log_id"],
            metadata["acquisition_started_at"],
            metadata["length_microseconds"],
            metadata["recording_started_at"],
        )
        cur.execute(INSERT_INTO_MANTARRAY_RECORDING_SESSIONS, recording_session_tuple)
    except Exception as e:
        raise Exception(f"in mantarray_recording_sessions: {e}")

    try:
        s3_object_tuple = (s3_size, metadata["file_creation_timestamp"], INFO_DICT["md5s"])
        cur.execute(INSERT_INTO_S3_OBJECTS, s3_object_tuple)
    except Exception as e:
        raise Exception(f"in s3_objects: {e}")

    try:
        log_session_key = "%s/%s.zip" % (customer_account_id, metadata["log_session_uuid"])
        session_log_tuple = (
            metadata["session_log_id"],
            LOGS_BUCKET,
            log_session_key,
            metadata["software_version"],
            metadata["file_format_version"],
            metadata["log_session_started_at"],
            customer_account_id,
            user_account_id,
        )
        cur.execute(INSERT_INTO_MANTARRAY_SESSION_LOG_FILES, session_log_tuple)
    except Exception as e:
        raise Exception(f"in mantarray_session_log_files: {e}")

    logger.info("Executing queries to the database in relation individual well data")
    try:
        for well in well_data:
            well_tuple = (
                well["well_index"],
                well["length_microseconds"],
                well["recording_started_at"],
                metadata["mantarray_recording_session_id"],
            )
            cur.execute(INSERT_INTO_MANTARRAY_RAW_FILES, well_tuple)
    except Exception as e:
        raise Exception(f"in mantarray_raw_files: {e}")

    conn.commit()


def set_info_dict(args):
    # Retrieve DB creds
    username, password = get_ssm_secrets()
    INFO_DICT["db_username"] = username
    INFO_DICT["db_password"] = password
    INFO_DICT["db_name"] = "mantarray_recordings"
    INFO_DICT["sdk_analysis_key"] = args[0]
    INFO_DICT["sdk_xlsx"] = args[1]
    INFO_DICT["pr"] = args[2]
    INFO_DICT["md5s"] = args[3]

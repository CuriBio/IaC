# from io import StringIO
import logging
import sys

import pymysql

from .aws_utils import get_s3_object_contents
from .aws_utils import get_ssm_secrets
from .helpers import load_data_to_dataframe
from .queries import INSERT_INT0_UPLOADED_S3_OBJECTS
from .queries import INSERT_INTO_MANTARRAY_RAW_FILES
from .queries import INSERT_INTO_MANTARRAY_RECORDING_SESSIONS
from .queries import INSERT_INTO_S3_OBJECTS


# set up custom basic config
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO, stream=sys.stdout
)
logger = logging.getLogger(__name__)

INFO_DICT = {}


def handle_db_metadata_insertions(bucket: str, key: str, db_host: str, args: list):
    """
    args:
        contains <file>.xlsx, individual well data, and the md5 hash
    """

    if not INFO_DICT:
        set_info_dict()

    try:
        conn = pymysql.connect(
            host=db_host,
            user=INFO_DICT["db_username"],
            passwd=INFO_DICT["db_password"],
            db=INFO_DICT["db_name"],
        )
        logger.info("Successful connection to Aurora database")
    except Exception as e:
        raise Exception(f"failed db connection: {e}")

    metadata, well_data = load_data_to_dataframe(args[0], args[1])
    s3_size = get_s3_object_contents(bucket, key)
    customer_account_id = key.split("/")[0]
    user_account_id = key.split("/")[1]

    cur = conn.cursor()

    try:
        uploaded_s3_tuple = (
            bucket,
            key,
            metadata["uploading_computer_name"],
        )
        cur.execute(INSERT_INT0_UPLOADED_S3_OBJECTS, uploaded_s3_tuple)

        recording_session_tuple = (
            metadata["mantarray_recording_session_id"],
            customer_account_id,
            user_account_id,
            metadata["instrument_serial_number"],
            metadata["acquisition_started_at"],
            metadata["length_microseconds"],
            metadata["recording_started_at"],
        )
        cur.execute(INSERT_INTO_MANTARRAY_RECORDING_SESSIONS, recording_session_tuple)

        s3_object_tuple = (s3_size, metadata["file_creation_timestamp"], args[2])
        cur.execute(INSERT_INTO_S3_OBJECTS, s3_object_tuple)

        logger.info("Executing queries to the database in relation to aggregated metadata")
    except Exception as e:
        raise Exception(f"in aggregated metadata: {e}")

    try:
        for well in well_data:
            well_tuple = (
                well["well_index"],
                well["length_microseconds"],
                well["recording_started_at"],
                metadata["mantarray_recording_session_id"],
            )
            cur.execute(INSERT_INTO_MANTARRAY_RAW_FILES, well_tuple)

        logger.info("Executing queries to the database in relation individual well data")
    except Exception as e:
        raise Exception(f"in individual well data: {e}")

    conn.commit()


def set_info_dict():
    # Retrieve DB creds
    username, password = get_ssm_secrets()
    INFO_DICT["db_username"] = username
    INFO_DICT["db_password"] = password
    INFO_DICT["db_name"] = "mantarray_recordings"

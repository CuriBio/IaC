import base64
import hashlib
import json
import logging
import os
import sys
import tempfile
from time import sleep
from urllib.parse import unquote_plus

import boto3
from botocore.exceptions import ClientError
from lib import main
from pulse3D.excel_writer import write_xlsx
from pulse3D.plate_recording import PlateRecording


SQS_URL = os.environ.get("SQS_URL")
SDK_ANALYZED_BUCKET = os.environ.get("SDK_ANALYZED_BUCKET")
SDK_STATUS_TABLE = os.environ.get("SDK_STATUS_TABLE")

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


def update_sdk_status(db_client, upload_id, new_status):
    try:
        db_client.update_item(
            TableName=SDK_STATUS_TABLE,
            Key={"upload_id": {"S": upload_id}},
            UpdateExpression="SET sdk_status = :val",
            ExpressionAttributeValues={":val": {"S": new_status}},
            ConditionExpression="attribute_exists(upload_id)",
        )
    except ClientError as e:
        logger.error(f"Error: {e}")
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            logger.error(f"Upload ID: {upload_id} was not found in table {SDK_STATUS_TABLE}")
            db_client.put_item(
                TableName=SDK_STATUS_TABLE,
                Item={"upload_id": {"S": upload_id}, "sdk_status": {"S": new_status}},
            )


def process_record(record, s3_client, db_client):
    bucket = record["s3"]["bucket"]["name"]
    obj_key = record["s3"]["object"]["key"]
    key = unquote_plus(obj_key)
    # retrieve metadata of file to be analyzed
    try:
        logger.info(f"Retrieving Head Object of {bucket}/{key}")
        upload_id = s3_client.head_object(Bucket=bucket, Key=key)["Metadata"]["upload-id"]

    except ClientError as e:
        logger.error(f"Error occurred while retrieving head object of {bucket}/{key}: {e}")
        return

    # a directory is needed to temporarily store files while running SDK analysis
    with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
        # handle H5 file download
        try:
            base_filename = key.rsplit("/", 1)[1]
            logger.info(f"Download {bucket}/{key} to {tmpdir}/{base_filename}")
            s3_client.download_file(bucket, key, f"{tmpdir}/{base_filename}")
        except Exception as e:
            logger.error(f"Failed to download {bucket}/{key}: {e}")
            update_sdk_status(db_client, upload_id, "error accessing file")
            return

        # handle running sdk analysis
        try:
            update_sdk_status(db_client, upload_id, "analysis running")
            file_name = f'{base_filename.split(".")[0]}.xlsx'
            recordings = PlateRecording.from_directory(tmpdir)
            pr = next(recordings)
            write_xlsx(pr, name=file_name)
        except Exception as e:
            logger.error(f"SDK analysis failed: {e}")
            update_sdk_status(db_client, upload_id, "error during analysis")
            return

        # handle xlsx file upload
        try:
            s3_analysis_key = f'{key.split(".")[0]}.xlsx'

            with open(f"{file_name}", "rb") as f:
                contents = f.read()
                md5 = hashlib.md5(contents).digest()
                md5s = base64.b64encode(md5).decode()
                s3_client.put_object(Body=f, Bucket=SDK_ANALYZED_BUCKET, Key=s3_analysis_key, ContentMD5=md5s)
            update_sdk_status(db_client, upload_id, "analysis complete")
        except Exception as e:
            logger.error(f"S3 Upload failed for {file_name} to {SDK_ANALYZED_BUCKET}/{s3_analysis_key}: {e}")
            update_sdk_status(db_client, upload_id, "error during upload of analyzed file")
            return

        # insert metadata into db
        try:
            logger.info(f"Inserting {file_name} metadata into aurora database")
            with open(f"{file_name}", "rb") as file:
                main.handle_db_metadata_insertions(pr, file, s3_analysis_key, md5s)
            update_sdk_status(db_client, upload_id, "analysis successfully inserted into database")
        except Exception as e:
            logger.error(f"Recording metadata failed to store in aurora database: {e}")
            update_sdk_status(db_client, upload_id, "error inserting analysis to database")
            return

        # generate presigned url to download .xlsx file
        try:
            logger.info(f"Generating presigned url for {SDK_ANALYZED_BUCKET}/{s3_analysis_key}")
            url = s3_client.generate_presigned_url(
                ClientMethod="get_object",
                Params={"Bucket": SDK_ANALYZED_BUCKET, "Key": s3_analysis_key},
                ExpiresIn=3600,
            )
            update_sdk_status(db_client, upload_id, url)
        except Exception as e:
            logger.error(f"Unable to generate presigned url for {SDK_ANALYZED_BUCKET}/{s3_analysis_key}: {e}")
            update_sdk_status(db_client, upload_id, "error generating presigned url")


def handler(max_num_loops=None):
    sqs_client = boto3.client("sqs")
    s3_client = boto3.client("s3")
    db_client = boto3.client("dynamodb")
    logger.info(f"Receiving messages on {SQS_URL}")

    num_loops = 0
    while True:
        try:
            sqs_response = sqs_client.receive_message(
                QueueUrl=SQS_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10
            )
            sqs_messages = sqs_response.get("Messages", [])
            if sqs_messages:
                log_msg = "Received {num_message} message"
                if len(sqs_messages) > 1:
                    log_msg += "s"
                logger.info(log_msg)

            for message in sqs_messages:
                message_body = json.loads(message.get("Body", r"{}"))
                record_list = message_body.get("Records", [])
                logger.info(f"Message contains {len(record_list)} records")
                for record in record_list:
                    if (
                        record.get("eventSource") == "aws:s3"
                        and record.get("eventName") == "ObjectCreated:Post"
                    ):
                        process_record(record, s3_client, db_client)
                    else:
                        logger.info("Skipping record")
                sqs_client.delete_message(QueueUrl=SQS_URL, ReceiptHandle=message["ReceiptHandle"])
        except ClientError as e:
            logger.exception(f"receive_message failed. Error: {e}")

        # conditional breaking of loop for unit testing
        if max_num_loops is not None:
            num_loops += 1
            if num_loops >= max_num_loops:
                return

        sleep(5)


if __name__ == "__main__":
    handler()

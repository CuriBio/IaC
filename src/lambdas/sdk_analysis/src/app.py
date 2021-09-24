import json
import logging
import os
import tempfile
import time

import boto3
from botocore.exceptions import ClientError
from curibio.sdk import PlateRecording
from .lib.helpers import handle_db_metadata_insertions
import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))


SQS_URL = os.environ.get("SQS_URL")
S3_UPLOAD_BUCKET = os.environ.get("S3_UPLOAD_BUCKET")


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    sqs_client = boto3.client("sqs")
    s3_client = boto3.client("s3")
    logger.info(f"Receiving messages on {SQS_URL}")

    while True:
        try:
            sqs_response = sqs_client.receive_message(
                QueueUrl=SQS_URL, MaxNumberOfMessages=1, WaitTimeSeconds=10
            )
            logger.info(f'Received: {len(sqs_response.get("Messages", []))}')

            for message in sqs_response.get("Messages", []):
                message_body = json.loads(message.get("Body", {}))
                if message_body:
                    for record in message_body.get("Records", []):
                        if (
                            record.get("eventSource") == "aws:s3"
                            and record.get("eventName") == "ObjectCreated:Post"
                        ):
                            bucket = record["s3"]["bucket"]["name"]
                            key = record["s3"]["object"]["key"]

                            with tempfile.TemporaryDirectory(dir="/tmp") as tmpdir:
                                try:
                                    logger.info(f"Download to {bucket}/{key} to {tmpdir}/{key}")
                                    s3_client.download_file(bucket, key, f"{tmpdir}/{key}")
                                except Exception as e:
                                    logger.error(f"Failed to download {bucket}/{key}: {e}")
                                    continue

                                try:
                                    file_name = f'{key.split(".")[0]}.xlsx'
                                    r = PlateRecording.from_directory(tmpdir)
                                    r.write_xlsx(tmpdir, file_name=file_name)
                                except Exception as e:
                                    logger.error(f"SDK analysis failed: {e}")
                                    continue

                                try:
                                    with open(f"{tmpdir}/{file_name}", "rb") as f:
                                        s3_client.upload_fileobj(f, S3_UPLOAD_BUCKET, file_name)
                                except Exception as e:
                                    logger.error(
                                        f"S3 Upload failed for {tmpdir}/{file_name} to {S3_UPLOAD_BUCKET}/{file_name}: {e}"
                                    )

                                try:
                                    logger.info(
                                        f"Inserting {tmpdir}/{file_name} metadata into aurora database"
                                    )
                                    with open(f"{tmpdir}/{file_name}", "rb") as file:
                                        handle_db_metadata_insertions(bucket, key, file, r)
                                except Exception as e:
                                    logger.error(
                                        f"Recording metadata failed to store in aurora database: {e}"
                                    )

                sqs_client.delete_message(QueueUrl=SQS_URL, ReceiptHandle=message["ReceiptHandle"])
        except ClientError:
            logger.exception("receive_message failed")

        time.sleep(5)

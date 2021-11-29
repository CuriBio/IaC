import json
import logging
import os
import sys

import boto3

S3_BUCKET = os.environ.get("S3_BUCKET")

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


def get_download_url(version: str):
    s3_client = boto3.client("s3")

    file_name = f"{version.replace('.', '_')}.bin"
    try:
        logger.info(f"Generating presigned url for {S3_BUCKET}/{file_name}")
        return s3_client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": S3_BUCKET, "Key": file_name}, ExpiresIn=3600,
        )
    except Exception as e:
        logger.error(f"Unable to generate presigned url for {S3_BUCKET}/{file_name}: {repr(e)}")
        return None


def handler(event, context):
    logger.info(f"event: {event}")

    try:
        firmware_version = event["queryStringParameters"]["firmware_version"]
    except (KeyError, TypeError):
        logger.exception("Request missing firmware_version param")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing firmware_version param"}),
        }

    url = get_download_url(firmware_version)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_url": url}),
    }

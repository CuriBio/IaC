import json
import logging
import os
import sys

import boto3

S3_MAIN_BUCKET = os.environ.get("S3_MAIN_BUCKET")
S3_CHANNEL_BUCKET = os.environ.get("S3_CHANNEL_BUCKET")

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


def get_download_url(version: str, bucket: str):
    s3_client = boto3.client("s3")

    file_name = f"{version.replace('.', '_')}.bin"
    try:
        logger.info(f"Generating presigned url for {bucket}/{file_name}")
        return s3_client.generate_presigned_url(
            ClientMethod="get_object", Params={"Bucket": bucket, "Key": file_name}, ExpiresIn=3600,
        )
    except Exception as e:
        logger.error(f"Unable to generate presigned url for {bucket}/{file_name}: {repr(e)}")
        return None


def handler(event, context):
    logger.info(f"event: {event}")

    try:
        firmware_version = event["queryStringParameters"]["firmware_version"]
        firmware_type = event["queryStringParameters"]["firmware_type"]
    except (KeyError, TypeError) as e:
        if isinstance(e, TypeError):
            missing_param = "firmware_version"
        else:
            missing_param = str(e)[1:-1]
            if "queryStringParameters" in missing_param:
                missing_param = "firmware_version"
        logger.exception(f"Request missing {missing_param} param")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Missing {missing_param} param"}),
        }

    if firmware_type == "main":
        bucket = S3_MAIN_BUCKET
    elif firmware_type == "channel":
        bucket = S3_CHANNEL_BUCKET
    else:
        err_msg = f"Invalid firmware type: {firmware_type}"
        logger.exception(err_msg)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": err_msg}),
        }

    url = get_download_url(firmware_version, bucket)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_url": url}),
    }

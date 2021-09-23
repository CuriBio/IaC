import json
import logging
import os
import sys

import boto3


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


def get_status(upload_id: str):
    db_client = boto3.client("dynamodb")
    db_response = db_client.get_item(TableName=SDK_STATUS_TABLE, Key={"upload_id": {"S": upload_id}})
    try:
        item = db_response["Item"]
    except KeyError:
        return None
    status = list(item["sdk_status"].values())[0]
    return status


def handler(event, context):
    logger.info(f"event: {event}")

    try:
        upload_id = event["queryStringParameters"]["upload_id"]
    except (KeyError, TypeError):
        logger.exception("Request missing upload_id param")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing upload_id param"}),
        }

    status = get_status(upload_id)
    if status is None:
        logger.exception(f"invalid upload_id: {upload_id}")
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Invalid upload_id: {upload_id}"}),
        }
    logger.info(f"Found status: {status} for upload_id: {upload_id}")  # TODO
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": status}),
    }

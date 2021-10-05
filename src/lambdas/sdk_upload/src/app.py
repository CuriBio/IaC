import json
import logging
import os
import sys
import uuid
import hashlib

import boto3
from botocore.exceptions import ClientError


S3_BUCKET = os.environ.get("S3_BUCKET")
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


def generate_presigned_params(s3_client, object_key, expires_in):
    upload_id = str(uuid.uuid4())
    md5s = hashlib.md5().hexdigest()
    fields = {"x-amz-meta-upload-id": upload_id, "Content-MD5": md5s}
    conditions = [{"x-amz-meta-upload-id": upload_id}]

    try:
        params = s3_client.generate_presigned_post(
            S3_BUCKET, object_key, Fields=fields, Conditions=conditions, ExpiresIn=expires_in
        )
        logger.info(f"Got presigned URL params: {params}")
    except ClientError:
        logger.exception("Couldn't get presigned URL params")
        raise

    return params, upload_id


def handler(event, context):
    s3_client = boto3.client("s3")

    logger.info(f"event: {event}")
    event_body = json.loads(event["body"])
    try:
        file_name = event_body["file_name"]
    except KeyError:
        logger.exception("file_name not found in request body")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing file_name"}),
        }

    presigned_params, upload_id = generate_presigned_params(s3_client, object_key=file_name, expires_in=3600)

    db_client = boto3.client("dynamodb")
    db_client.put_item(
        TableName=SDK_STATUS_TABLE,
        Item={"upload_id": {"S": upload_id}, "sdk_status": {"S": "analysis pending"}},
        ConditionExpression="attribute_not_exists(upload_id)",
    )

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_params": presigned_params, "upload_id": upload_id}),
    }

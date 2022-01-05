import json
import logging
import os
import sys
import uuid

import boto3
from botocore.exceptions import ClientError

SDK_UPLOAD_BUCKET = os.environ.get("SDK_UPLOAD_BUCKET")
LOGS_BUCKET = os.environ.get("LOGS_BUCKET")
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


def generate_presigned_params_for_sdk(s3_client, md5s, object_key, expires_in):
    upload_id = str(uuid.uuid4())

    fields = {"x-amz-meta-upload-id": upload_id, "Content-MD5": md5s}
    conditions = [{"x-amz-meta-upload-id": upload_id}, ["starts-with", "$Content-MD5", ""]]

    try:
        params = s3_client.generate_presigned_post(
            SDK_UPLOAD_BUCKET, object_key, Fields=fields, Conditions=conditions, ExpiresIn=expires_in
        )
        logger.info(f"Got presigned URL params for an sdk upload: {params}")
    except ClientError:
        logger.exception("Couldn't get presigned URL params for an sdk upload")
        raise

    try:
        db_client = boto3.client("dynamodb")
        db_client.put_item(
            TableName=SDK_STATUS_TABLE,
            Item={"upload_id": {"S": upload_id}, "sdk_status": {"S": "analysis pending"}},
            ConditionExpression="attribute_not_exists(upload_id)",
        )
    except ClientError:
        logger.exception("Could not update upload status after generating a presigned post")
        raise

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_params": params, "upload_id": upload_id}),
    }


def generate_presigned_params_for_logs(s3_client, md5s, object_key, expires_in):
    fields = {"Content-MD5": md5s}
    conditions = [["starts-with", "$Content-MD5", ""]]

    try:
        params = s3_client.generate_presigned_post(
            LOGS_BUCKET, object_key, Fields=fields, Conditions=conditions, ExpiresIn=expires_in
        )
        logger.info(f"Got presigned URL params for uploading mantarray logs: {params}")
    except ClientError:
        logger.exception("Couldn't get presigned URL params for uploading log files")
        raise

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_params": params}),
    }


def handler(event, context):
    s3_client = boto3.client("s3")
    logger.info(f"event: {event}")
    event_body = json.loads(event["body"])

    try:
        upload_type = event_body["upload_type"]
    except KeyError:
        logger.exception("upload_type not found in request body")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing upload_type"}),
        }

    try:
        file_name = event_body["file_name"]
    except KeyError:
        logger.exception("file_name not found in request body")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing file_name"}),
        }

    try:
        md5s = event["headers"]["Content-MD5"]
    except KeyError:
        logger.exception("Content-MD5 header not found in request")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing Content-MD5 header"}),
        }

    if upload_type == "sdk_upload":
        response = generate_presigned_params_for_sdk(s3_client, md5s, object_key=file_name, expires_in=3600)
    else:
        response = generate_presigned_params_for_logs(s3_client, md5s, object_key=file_name, expires_in=3600)

    return response

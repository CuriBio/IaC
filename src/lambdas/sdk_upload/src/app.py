import logging
import os

import boto3
from botocore.exceptions import ClientError


S3_BUCKET = os.environ.get("S3_BUCKET")

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_presigned_url(s3_client, object_key, expires_in):
    try:
        url = s3_client.generate_presigned_post(
            S3_BUCKET, object_key, Fields=None, Conditions=None, ExpiresIn=expires_in
        )
        logger.info(f"Got presigned URL: {url}")
    except ClientError:
        logger.exception("Couldn't get a presigned URL")
        raise

    return url


def handler(event, context):
    s3_client = boto3.client("s3")
    logger.info(f"event: {event}")
    url = generate_presigned_url(s3_client, object_key=event["file_name"], expires_in=3600)
    return {"status": "ok", "url": url}

import json
import logging
import os
import re
import sys

import boto3
from semver import VersionInfo

S3_MAIN_BUCKET = os.environ.get("S3_MAIN_BUCKET")
FIRMWARE_FILE_REGEX = re.compile(r"^\d+\_\d+_\d+\.bin$")

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


def get_version_info(version_str):
    return VersionInfo.parse(".".join(version_str.split("_")))


def get_latest_firmware_version(software_version: str):
    software_version_info = VersionInfo.parse(software_version)

    s3_client = boto3.client("s3")
    firmware_bucket_objs = s3_client.list_objects(Bucket=S3_MAIN_BUCKET)
    firmware_file_names = [
        item["Key"] for item in firmware_bucket_objs["Contents"] if FIRMWARE_FILE_REGEX.search(item["Key"])
    ]
    compatible_firmware_files = set(firmware_file_names)
    for file_name in firmware_file_names:
        head_obj = s3_client.head_object(Bucket=S3_MAIN_BUCKET, Key=file_name)
        max_software_version = head_obj["Metadata"].get("max-software-version", None)
        min_software_version = head_obj["Metadata"]["min-software-version"]
        is_firmware_version_incompatible = software_version_info < VersionInfo.parse(min_software_version)
        if max_software_version is not None:
            is_firmware_version_incompatible |= software_version_info > VersionInfo.parse(
                max_software_version
            )
        if is_firmware_version_incompatible:
            compatible_firmware_files.remove(file_name)

    compatible_firmware_versions = [file_name.split(".")[0] for file_name in compatible_firmware_files]
    if len(compatible_firmware_files) == 0:
        logger.info("No compatible firmware versions found")
        return None
    latest_firmware_version = sorted(compatible_firmware_versions, key=get_version_info)[-1].replace("_", ".")
    return latest_firmware_version


def handler(event, context):
    logger.info(f"event: {event}")

    try:
        software_version = event["queryStringParameters"]["software_version"]
    except (KeyError, TypeError):
        logger.exception("Request missing software_version param")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing software_version param"}),
        }

    latest_firmware_version = get_latest_firmware_version(software_version)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_version": latest_firmware_version}),
    }

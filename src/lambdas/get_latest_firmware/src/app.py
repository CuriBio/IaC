import json
import logging
import os
import re
import sys

import boto3
from semver import VersionInfo

S3_MAIN_BUCKET = os.environ.get("S3_MAIN_BUCKET")
S3_CHANNEL_BUCKET = os.environ.get("S3_CHANNEL_BUCKET")
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


def get_latest_firmware_versions(software_version: str, main_firmware_version: str):
    software_version_info = VersionInfo.parse(software_version)
    main_firmware_version_info = VersionInfo.parse(main_firmware_version)

    latest_firmware_versions = {}
    s3_client = boto3.client("s3")
    for firmware_type, current_version_info, bucket, validation_type in (
        ("main", software_version_info, S3_MAIN_BUCKET, "software"),
        ("channel", main_firmware_version_info, S3_CHANNEL_BUCKET, "main-firmware"),
    ):
        firmware_bucket_objs = s3_client.list_objects(Bucket=bucket)
        firmware_file_names = [
            item["Key"]
            for item in firmware_bucket_objs["Contents"]
            if FIRMWARE_FILE_REGEX.search(item["Key"])
        ]
        compatible_firmware_files = set(firmware_file_names)
        for file_name in firmware_file_names:
            head_obj = s3_client.head_object(Bucket=bucket, Key=file_name)
            max_version = head_obj["Metadata"].get(f"max-{validation_type}-version", None)
            min_version = head_obj["Metadata"][f"min-{validation_type}-version"]
            is_firmware_version_incompatible = current_version_info < VersionInfo.parse(min_version)
            if max_version is not None:
                is_firmware_version_incompatible |= current_version_info > VersionInfo.parse(max_version)
            if is_firmware_version_incompatible:
                compatible_firmware_files.remove(file_name)

        compatible_firmware_versions = [file_name.split(".")[0] for file_name in compatible_firmware_files]
        if len(compatible_firmware_files) == 0:
            logger.info(f"No compatible {firmware_type} firmware versions found")
            latest_firmware_version = None
        else:
            latest_firmware_version = sorted(compatible_firmware_versions, key=get_version_info)[-1].replace(
                "_", "."
            )
        latest_firmware_versions[firmware_type] = latest_firmware_version
    return latest_firmware_versions


def handler(event, context):
    logger.info(f"event: {event}")

    try:
        software_version = event["queryStringParameters"]["software_version"]
        main_firmware_version = event["queryStringParameters"]["main_firmware_version"]
    except (KeyError, TypeError) as e:
        if isinstance(e, TypeError):
            missing_param = "software_version"
        else:
            missing_param = str(e)[1:-1]
            if "queryStringParameters" in missing_param:
                missing_param = "software_version"
        logger.exception(f"Request missing {missing_param} param")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Missing {missing_param} param"}),
        }

    latest_firmware_version = get_latest_firmware_versions(software_version, main_firmware_version)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_versions": latest_firmware_version}),
    }

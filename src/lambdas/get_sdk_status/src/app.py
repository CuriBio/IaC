import json
import logging
import sys


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
    # TODO:
    #   query DB for upload_id and return the status
    #   figure out if error will be raised if upload_id is not present in table. If not, then return some kind of error msg or raise an error
    return ""


def handler(event, context):
    logger.info(f"event: {event}")

    event_params = event["queryStringParameters"]
    try:
        upload_id = event_params["upload_id"]
    except KeyError:
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Missing upload_id param"}),
        }
    try:
        status = get_status(upload_id)
    except Exception as e:
        logger.info(f"Error: {e}")  # temp log to figure out what errors (if any) can come up here
        logger.info(f"invalid upload_id: {upload_id}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Invalid upload_id: {upload_id}"}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(status),
    }

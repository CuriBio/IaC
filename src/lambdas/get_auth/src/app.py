import json
import logging
import os
import sys

import boto3
from botocore.exceptions import ClientError


COGNITO_USER_POOL_CLIENT_ID = os.environ.get("COGNITO_USER_POOL_CLIENT_ID")


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


def get_tokens(username: str, password: str):
    client = boto3.client("cognito-idp")
    response = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId=COGNITO_USER_POOL_CLIENT_ID,
    )
    logger.info(f"initiate_auth response: {response}")

    result = response["AuthenticationResult"]
    return {
        "access_token": result["AccessToken"],
        "id_token": result["IdToken"],
        "refresh_token": result["RefreshToken"],
    }


def handler(event, context):
    logger.info(f"event: {event}")
    event_body = json.loads(event["body"])
    try:
        username = event_body["username"]
        password = event_body["password"]
    except KeyError as e:
        missing_cred = e.args[0]
        logger.exception(f"Request missing {missing_cred}")
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": f"Missing {missing_cred}"}),
        }

    try:
        token_dict = get_tokens(username, password)
    except ClientError as e:
        logger.exception(f"Error: {e}")
        return {
            "statusCode": 401,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Invalid credentials"}),
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(token_dict),
    }

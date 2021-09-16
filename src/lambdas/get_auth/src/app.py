import json
import logging
import sys

import boto3


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


# TODO add logging statements
def get_tokens(username: str, password: str):
    client = boto3.client("cognito-idp")
    response = client.initiate_auth(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": username, "PASSWORD": password},
        ClientId="TODO",
    )

    # response = {
    #     "ChallengeName": "SMS_MFA"|"SOFTWARE_TOKEN_MFA"|"SELECT_MFA_TYPE"|"MFA_SETUP"|"PASSWORD_VERIFIER"|"CUSTOM_CHALLENGE"|"DEVICE_SRP_AUTH"|"DEVICE_PASSWORD_VERIFIER"|"ADMIN_NO_SRP_AUTH"|"NEW_PASSWORD_REQUIRED",
    #     "Session": "string",
    #     "ChallengeParameters": {
    #         "string": "string"
    #     },
    #     "AuthenticationResult": {
    #         "AccessToken": "string",
    #         "ExpiresIn": 123,
    #         "TokenType": "string",
    #         "RefreshToken": "string",
    #         "IdToken": "string",
    #         "NewDeviceMetadata": {
    #             "DeviceKey": "string",
    #             "DeviceGroupKey": "string"
    #         }
    #     }
    # }

    result = response["AuthenticationResult"]
    return {
        "access_token": result["AccessToken"],
        "id_token": result["IdToken"],
        "refresh_token": result["RefreshToken"],
    }


def handler(event, context):
    event_body = json.loads(event["body"])
    try:
        token_dict = get_tokens(event_body["username"], event_body["password"])
    except:  # noqa
        return {
            "statusCode": 401,
        }

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(token_dict),
    }

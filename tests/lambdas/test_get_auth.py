import json

from botocore.exceptions import ClientError
import pytest

from ..test_utils import import_lambda

get_auth = import_lambda("get_auth")


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_cognito_idp_client = mocker.Mock()

    def se(client_type):
        if client_type == "cognito-idp":
            return mocked_cognito_idp_client

    mocker.patch.object(get_auth.boto3, "client", autospec=True, side_effect=se)

    yield mocked_cognito_idp_client


def test_get_auth__returns_error_code_when_username_not_given():
    response = get_auth.handler({"body": json.dumps({})}, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing username"}),
    }


def test_get_auth__returns_error_code_when_password_not_given():
    response = get_auth.handler({"body": json.dumps({"username": "usr"})}, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing password"}),
    }


@pytest.mark.parametrize("test_missing_cred", ["username", "password"])
def test_get_auth__logs_exception_when_credential_is_missing(test_missing_cred, mocker):
    spied_logger_exception = mocker.spy(get_auth.logger, "exception")

    test_body = {"username": "usr", "password": "pw"}
    del test_body[test_missing_cred]
    get_auth.handler({"body": json.dumps(test_body)}, None)
    spied_logger_exception.assert_called_once_with(f"Request missing {test_missing_cred}")


def test_get_auth__validates_credentials_correctly(mocker, mocked_boto3_client):
    mocked_cognito_idp_client = mocked_boto3_client

    mocked_cognito_idp_client.initiate_auth.return_value = {
        "AuthenticationResult": {"AccessToken": "", "IdToken": "", "RefreshToken": ""}
    }
    expected_client_id = "test_id"
    mocker.patch.object(get_auth, "COGNITO_USER_POOL_CLIENT_ID", expected_client_id)

    test_username = "test_user"
    test_password = "test_pw"
    get_auth.handler({"body": json.dumps({"username": test_username, "password": test_password})}, None)
    mocked_cognito_idp_client.initiate_auth.assert_called_once_with(
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters={"USERNAME": test_username, "PASSWORD": test_password},
        ClientId=expected_client_id,
    )


def test_get_auth__returns_correct_response_when_valid_credentials_are_given(mocked_boto3_client):
    mocked_cognito_idp_client = mocked_boto3_client

    expected_token_dict = {
        "access_token": "at",
        "id_token": "it",
        "refresh_token": "rt",
    }
    mocked_cognito_idp_client.initiate_auth.return_value = {
        "AuthenticationResult": {
            "AccessToken": expected_token_dict["access_token"],
            "IdToken": expected_token_dict["id_token"],
            "RefreshToken": expected_token_dict["refresh_token"],
        }
    }

    test_username = "test_user"
    test_password = "test_pw"
    response = get_auth.handler(
        {"body": json.dumps({"username": test_username, "password": test_password})}, None
    )
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(expected_token_dict),
    }


def test_get_auth__returns_error_code_and_logs_exception_when_invalid_credentials_given(
    mocker, mocked_boto3_client
):
    mocked_cognito_idp_client = mocked_boto3_client

    expected_error = ClientError({}, "")
    mocked_cognito_idp_client.initiate_auth.side_effect = expected_error

    spied_logger_exception = mocker.spy(get_auth.logger, "exception")

    response = get_auth.handler({"body": json.dumps({"username": "bad", "password": "wrong"})}, None)
    assert response == {
        "statusCode": 401,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Invalid credentials"}),
    }
    spied_logger_exception.assert_called_once_with(f"Error: {expected_error}")


def test_get_auth__handles_info_logging(mocker, mocked_boto3_client):
    mocked_cognito_idp_client = mocked_boto3_client

    expected_initiate_auth_response = {
        "AuthenticationResult": {"AccessToken": "at", "IdToken": "id", "RefreshToken": "rt"}
    }
    mocked_cognito_idp_client.initiate_auth.return_value = expected_initiate_auth_response
    spied_logger_info = mocker.spy(get_auth.logger, "info")

    test_username = "test_user"
    test_password = "test_pw"
    test_event = {"body": json.dumps({"username": test_username, "password": test_password})}
    get_auth.handler(test_event, None)
    spied_logger_info.assert_any_call(f"event: {test_event}")
    spied_logger_info.assert_any_call(f"initiate_auth response: {expected_initiate_auth_response}")

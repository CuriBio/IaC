import json

import pytest

from ..test_utils import import_lambda

get_sdk_status = import_lambda("get_sdk_status")


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_dynamodb_client = mocker.Mock()

    def se(client_type):
        if client_type == "dynamodb":
            return mocked_dynamodb_client

    mocker.patch.object(get_sdk_status.boto3, "client", autospec=True, side_effect=se)

    yield mocked_dynamodb_client


def test_get_sdk_status__returns_error_code_if_queryStringParameters_given_without_upload_id():
    response = get_sdk_status.handler({"queryStringParameters": {}}, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing upload_id param"}),
    }


def test_get_sdk_status__returns_error_code_if_queryStringParameters_not_given():
    response = get_sdk_status.handler({}, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing upload_id param"}),
    }


@pytest.mark.parametrize("test_event", [{}, {"queryStringParameters": {}}])
def test_get_sdk_status__logs_exception_if_upload_id_not_given(test_event, mocker):
    spied_logger_exception = mocker.spy(get_sdk_status.logger, "exception")
    get_sdk_status.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing upload_id param")


def test_get_sdk_status__gets_item_from_dynamodb_table_correctly(mocker, mocked_boto3_client):
    mocked_dynamodb_client = mocked_boto3_client
    mocked_dynamodb_client.get_item.return_value = {}

    expected_table_name = "test_table"
    mocker.patch.object(get_sdk_status, "SDK_STATUS_TABLE", expected_table_name)

    test_upload_id = "test_id"
    test_event = {"queryStringParameters": {"upload_id": test_upload_id}}
    get_sdk_status.handler(test_event, None)
    mocked_dynamodb_client.get_item.assert_called_once_with(
        TableName=expected_table_name, Key={"upload_id": {"S": test_upload_id}}
    )


def test_get_sdk_status__returns_correct_response_when_upload_id_is_found(mocked_boto3_client):
    mocked_dynamodb_client = mocked_boto3_client

    expected_status = "test status"
    mocked_dynamodb_client.get_item.return_value = {"Item": {"sdk_status": {"S": expected_status}}}

    test_upload_id = "test_id"
    test_event = {"queryStringParameters": {"upload_id": test_upload_id}}
    response = get_sdk_status.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"status": expected_status}),
    }


def test_get_sdk_status__returns_error_code_and_logs_exception_when_upload_id_not_found(
    mocker, mocked_boto3_client
):
    mocked_dynamodb_client = mocked_boto3_client
    mocked_dynamodb_client.get_item.return_value = {}

    spied_logger_exception = mocker.spy(get_sdk_status.logger, "exception")

    test_upload_id = "test_id"
    test_event = {"queryStringParameters": {"upload_id": test_upload_id}}
    response = get_sdk_status.handler(test_event, None)
    assert response == {
        "statusCode": 404,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": f"Invalid upload_id: {test_upload_id}"}),
    }
    spied_logger_exception.assert_called_once_with(f"invalid upload_id: {test_upload_id}")


def test_get_sdk_status__handles_info_logging(mocker, mocked_boto3_client):
    mocked_dynamodb_client = mocked_boto3_client

    expected_status = "test status"
    mocked_dynamodb_client.get_item.return_value = {"Item": {"sdk_status": {"S": expected_status}}}
    spied_logger_info = mocker.spy(get_sdk_status.logger, "info")

    test_upload_id = "test_id"
    test_event = {"queryStringParameters": {"upload_id": test_upload_id}}
    get_sdk_status.handler(test_event, None)

    spied_logger_info.assert_any_call(f"event: {test_event}")
    spied_logger_info.assert_any_call(f"Found status: {expected_status} for upload_id: {test_upload_id}")

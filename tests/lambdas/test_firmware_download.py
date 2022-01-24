import json

import pytest

from ..test_utils import import_lambda

firmware_download = import_lambda("firmware_download")


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_s3_client = mocker.Mock()

    def se(client_type):
        if client_type == "s3":
            return mocked_s3_client

    mocker.patch.object(firmware_download.boto3, "client", autospec=True, side_effect=se)

    yield mocked_s3_client


def test_firmware_download__logs_event(mocker):
    spied_logger_info = mocker.spy(firmware_download.logger, "info")

    test_event = {"queryStringParameters": {}}
    firmware_download.handler(test_event, None)
    spied_logger_info.assert_any_call(f"event: {test_event}")


@pytest.mark.parametrize(
    "test_event",
    [
        {},
        {"queryStringParameters": None},
        {"queryStringParameters": {}},
        {"queryStringParameters": {"firmware_type": "main"}},
    ],
)
def test_firmware_download__returns_error_code_if_firmware_version_not_given(test_event):
    response = firmware_download.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing firmware_version param"}),
    }


@pytest.mark.parametrize("test_event", [{}, {"queryStringParameters": None}, {"queryStringParameters": {}}])
def test_firmware_download__logs_exception_if_firmware_version_not_given(test_event, mocker):
    spied_logger_exception = mocker.spy(firmware_download.logger, "exception")
    firmware_download.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing firmware_version param")


def test_firmware_download__returns_error_code_if_firmware_type_not_given():
    test_event = {"queryStringParameters": {"firmware_version": "0.0.0"}}
    response = firmware_download.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing firmware_type param"}),
    }


def test_firmware_download__logs_exception_if_firmware_type_not_given(mocker):
    spied_logger_exception = mocker.spy(firmware_download.logger, "exception")
    test_event = {"queryStringParameters": {"firmware_version": "0.0.0"}}
    firmware_download.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing firmware_type param")


def test_firmware_download__returns_error_code_if_firmware_type_is_invalid():
    bad_firmware_type = "bad"
    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": bad_firmware_type}}
    response = firmware_download.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": f"Invalid firmware type: {bad_firmware_type}"}),
    }


def test_firmware_download__logs_exception_if_firmware_type_is_invalid(mocker):
    spied_logger_exception = mocker.spy(firmware_download.logger, "exception")

    bad_firmware_type = "bad"
    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": bad_firmware_type}}
    firmware_download.handler(test_event, None)
    spied_logger_exception.assert_called_once_with(f"Invalid firmware type: {bad_firmware_type}")


@pytest.mark.parametrize("firmware_type", ["main", "channel"])
def test_firmware_download__gets_presigned_url_correctly(firmware_type, mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.generate_presigned_url.return_value = "dummy.url"

    expected_main_bucket_name = "main_bucket"
    mocker.patch.object(firmware_download, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_bucket"
    mocker.patch.object(firmware_download, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": firmware_type}}
    firmware_download.handler(test_event, None)

    expected_bucket_name = (
        expected_main_bucket_name if firmware_type == "main" else expected_channel_bucket_name
    )
    mocked_s3_client.generate_presigned_url.assert_called_once_with(
        ClientMethod="get_object",
        Params={"Bucket": expected_bucket_name, "Key": "0.0.0.bin"},
        ExpiresIn=3600,
    )


@pytest.mark.parametrize("firmware_type", ["main", "channel"])
def test_firmware_download__returns_correct_response__if_presigned_url_successfully_generated(
    firmware_type, mocked_boto3_client,
):
    mocked_s3_client = mocked_boto3_client

    expected_url = "expected.url"
    mocked_s3_client.generate_presigned_url.return_value = expected_url

    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": firmware_type}}
    response = firmware_download.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_url": expected_url}),
    }


@pytest.mark.parametrize("firmware_type", ["main", "channel"])
def test_firmware_download__returns_correct_response__if_presigned_url_generation_fails(
    firmware_type, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.generate_presigned_url.side_effect = Exception

    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": firmware_type}}
    response = firmware_download.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_url": None}),
    }


@pytest.mark.parametrize("firmware_type", ["main", "channel"])
def test_firmware_download__logs_error__if_presigned_url_generation_fails(
    firmware_type, mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client

    expected_error = Exception("error msg")
    mocked_s3_client.generate_presigned_url.side_effect = expected_error

    expected_main_bucket_name = "main_bucket"
    mocker.patch.object(firmware_download, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_bucket"
    mocker.patch.object(firmware_download, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    spied_logger_error = mocker.spy(firmware_download.logger, "error")

    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": firmware_type}}
    firmware_download.handler(test_event, None)

    expected_bucket_name = (
        expected_main_bucket_name if firmware_type == "main" else expected_channel_bucket_name
    )
    spied_logger_error.assert_called_once_with(
        f"Unable to generate presigned url for {expected_bucket_name}/0.0.0.bin: {repr(expected_error)}"
    )


@pytest.mark.parametrize("firmware_type", ["main", "channel"])
def test_firmware_download__logs_info(firmware_type, mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.generate_presigned_url.return_value = "dummy.url"

    expected_main_bucket_name = "main_bucket"
    mocker.patch.object(firmware_download, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_bucket"
    mocker.patch.object(firmware_download, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    spied_logger_info = mocker.spy(firmware_download.logger, "info")

    test_event = {"queryStringParameters": {"firmware_version": "0.0.0", "firmware_type": firmware_type}}
    firmware_download.handler(test_event, None)

    expected_bucket_name = (
        expected_main_bucket_name if firmware_type == "main" else expected_channel_bucket_name
    )
    spied_logger_info.assert_any_call(f"Generating presigned url for {expected_bucket_name}/0.0.0.bin")

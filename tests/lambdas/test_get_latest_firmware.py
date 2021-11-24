import json

import pytest

from ..test_utils import import_lambda

get_latest_firmware = import_lambda("get_latest_firmware")


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_s3_client = mocker.Mock()

    def se(client_type):
        if client_type == "s3":
            return mocked_s3_client

    mocker.patch.object(get_latest_firmware.boto3, "client", autospec=True, side_effect=se)

    yield mocked_s3_client


def test_get_latest_firmware__returns_error_code_if_queryStringParameters_given_without_software_version():
    response = get_latest_firmware.handler({"queryStringParameters": {}}, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing software_version param"}),
    }


def test_get_latest_firmware__logs_event(mocker):
    spied_logger_info = mocker.spy(get_latest_firmware.logger, "info")

    test_event = {"queryStringParameters": {}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_info.assert_any_call(f"event: {test_event}")


@pytest.mark.parametrize("test_event", [{}, {"queryStringParameters": {}}])
def test_get_latest_firmware__logs_exception_if_software_version_not_given(test_event, mocker):
    spied_logger_exception = mocker.spy(get_latest_firmware.logger, "exception")
    get_latest_firmware.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing software_version param")


def test_get_latest_firmware__gets_firmware_file_objects_from_s3_correctly(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    expected_bucket_name = "test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_BUCKET", expected_bucket_name)

    test_event = {"queryStringParameters": {"software_version": "0.0.0"}}
    get_latest_firmware.handler(test_event, None)

    mocked_s3_client.list_objects.assert_called_once_with(Bucket=expected_bucket_name)


def test_get_latest_firmware__retrieves_metadata_of_each_correctly_named_firmware_file_in_s3_bucket_correctly(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client

    expected_valid_file_names = ["0_0_0.bin", "99_99_99.bin"]
    test_file_names = [
        "x1_0_0.bin",
        "x_0_0.bin",
        "1_x_0.bin",
        "1_0_x.bin",
        "1_0_0,bin",
        "1_0_0.bit",
        "1_0_0.binx",
    ]
    test_file_names.extend(expected_valid_file_names)
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }

    mocked_s3_client.head_object.return_value = {
        "Metadata": {"max-software-version": "0.0.0", "min-software-version": "0.0.0"}
    }

    expected_bucket_name = "test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_BUCKET", expected_bucket_name)

    test_event = {"queryStringParameters": {"software_version": "1.0.0"}}
    get_latest_firmware.handler(test_event, None)

    assert mocked_s3_client.head_object.call_args_list == [
        mocker.call(Bucket=expected_bucket_name, Key=file_name) for file_name in expected_valid_file_names
    ]


def test_get_latest_firmware__logs_info__if_no_compatible_firmware_files_found(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    spied_logger_info = mocker.spy(get_latest_firmware.logger, "info")

    test_event = {"queryStringParameters": {"software_version": "1.0.0"}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_info.assert_any_call("No compatible firmware versions found")


@pytest.mark.parametrize("min_sv,max_sv", [("1.0.1", "1.0.1"), ("0.9.9", "0.9.9")])
def test_get_latest_firmware__returns_correct_response__if_no_compatible_firmware_files_found(
    mocked_boto3_client, min_sv, max_sv
):
    mocked_s3_client = mocked_boto3_client

    test_file_names = ["1_0_0.bin", "1_0_1.bin", "1_1_0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }
    mocked_s3_client.head_object.return_value = {
        "Metadata": {"max-software-version": max_sv, "min-software-version": min_sv}
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_version": None}),
    }


def test_get_latest_firmware__returns_correct_response__when_multiple_compatible_firmware_files_found(
    mocked_boto3_client,
):
    mocked_s3_client = mocked_boto3_client

    test_file_names = ["0_9_9.bin", "1_0_0.bin", "1_0_1.bin", "1_1_0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }

    test_software_versions = {
        "0_9_9.bin": {"min-software-version": "0.0.0", "max-software-version": "0.0.0"},
        "1_0_0.bin": {"min-software-version": "0.9.9", "max-software-version": "1.0.0"},
        "1_0_1.bin": {"min-software-version": "1.0.0", "max-software-version": "1.0.1"},
        "1_1_0.bin": {"min-software-version": "2.0.0", "max-software-version": "2.0.0"},
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {"Metadata": test_software_versions[Key]}

    test_event = {"queryStringParameters": {"software_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_version": "1.0.1"}),
    }


def test_get_latest_firmware__returns_correct_response__when_multiple_compatible_firmware_files_found__with_no_max_software_version(
    mocked_boto3_client,
):
    mocked_s3_client = mocked_boto3_client

    test_file_names = ["0_9_9.bin", "1_0_0.bin", "1_0_1.bin", "1_1_0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }

    test_software_versions = {
        "0_9_9.bin": {"min-software-version": "0.0.0", "max-software-version": "0.0.0"},
        "1_0_0.bin": {"min-software-version": "0.9.9"},
        "1_0_1.bin": {"min-software-version": "1.0.0"},
        "1_1_0.bin": {"min-software-version": "2.0.0"},
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {"Metadata": test_software_versions[Key]}

    test_event = {"queryStringParameters": {"software_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_version": "1.0.1"}),
    }

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


def test_get_latest_firmware__logs_event(mocker):
    spied_logger_info = mocker.spy(get_latest_firmware.logger, "info")

    test_event = {"queryStringParameters": {}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_info.assert_any_call(f"event: {test_event}")


@pytest.mark.parametrize("test_event", [{}, {"queryStringParameters": None}, {"queryStringParameters": {}}])
def test_get_latest_firmware__returns_error_code_if_software_version_not_given(test_event):
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing software_version param"}),
    }


@pytest.mark.parametrize(
    "test_event",
    [
        {},
        {"queryStringParameters": None},
        {"queryStringParameters": {}},
        {"queryStringParameters": {"main_firmware_version": "0.0.0"}},
    ],
)
def test_get_latest_firmware__logs_exception_if_software_version_not_given(test_event, mocker):
    spied_logger_exception = mocker.spy(get_latest_firmware.logger, "exception")
    get_latest_firmware.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing software_version param")


def test_get_latest_firmware__returns_error_code_if_main_firmware_version_not_given():
    test_event = {"queryStringParameters": {"software_version": "0.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing main_firmware_version param"}),
    }


def test_get_latest_firmware__logs_exception_if_main_firmware_version_not_given(mocker):
    spied_logger_exception = mocker.spy(get_latest_firmware.logger, "exception")
    test_event = {"queryStringParameters": {"software_version": "0.0.0"}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing main_firmware_version param")


def test_get_latest_firmware__gets_firmware_file_objects_from_s3_correctly(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    expected_main_bucket_name = "main_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_event = {"queryStringParameters": {"software_version": "0.0.0", "main_firmware_version": "0.0.0"}}
    get_latest_firmware.handler(test_event, None)

    assert mocked_s3_client.list_objects.call_count == 2
    mocked_s3_client.list_objects.assert_any_call(Bucket=expected_main_bucket_name)
    mocked_s3_client.list_objects.assert_any_call(Bucket=expected_channel_bucket_name)


def test_get_latest_firmware__retrieves_metadata_of_each_correctly_named_firmware_file_in_s3_bucket_correctly(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    expected_valid_main_file_names = ["0_0_0.bin", "99_99_99.bin"]
    expected_valid_channel_file_names = ["0_9_9.bin", "99_88_0.bin"]

    def se(Bucket):
        test_file_names = [
            "x1_0_0.bin",
            "x_0_0.bin",
            "1_x_0.bin",
            "1_0_x.bin",
            "1_0_0,bin",
            "1_0_0.bit",
            "1_0_0.binx",
        ]
        if Bucket == expected_main_bucket_name:
            test_file_names.extend(expected_valid_main_file_names)
        else:
            test_file_names.extend(expected_valid_channel_file_names)
        return {"Contents": [{"Key": file_name} for file_name in test_file_names]}

    mocked_s3_client.list_objects.side_effect = se
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            {"max-software-version": "0.0.0", "min-software-version": "0.0.0"}
            if Bucket == expected_main_bucket_name
            else {"max-main-firmware-version": "0.0.0", "min-main-firmware-version": "0.0.0"}
        )
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    get_latest_firmware.handler(test_event, None)

    expected_calls = [
        mocker.call(Bucket=expected_main_bucket_name, Key=file_name)
        for file_name in expected_valid_main_file_names
    ]
    expected_calls.extend(
        [
            mocker.call(Bucket=expected_channel_bucket_name, Key=file_name)
            for file_name in expected_valid_channel_file_names
        ]
    )
    assert mocked_s3_client.head_object.call_args_list == expected_calls


def test_get_latest_firmware__logs_info__if_no_compatible_firmware_files_found(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    spied_logger_info = mocker.spy(get_latest_firmware.logger, "info")

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_info.assert_any_call("No compatible main firmware versions found")
    spied_logger_info.assert_any_call("No compatible channel firmware versions found")


@pytest.mark.parametrize("min_sv,max_sv", [("1.0.1", "1.0.1"), ("0.9.9", "0.9.9")])
def test_get_latest_firmware__returns_correct_response__if_no_compatible_main_firmware_files_found(
    min_sv, max_sv, mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_file_names = ["1_0_0.bin", "1_0_1.bin", "1_1_0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            {"max-software-version": max_sv, "min-software-version": min_sv}
            if Bucket == expected_main_bucket_name
            else {"max-main-firmware-version": "1.0.0", "min-main-firmware-version": "1.0.0"}
        )
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_versions": {"main": None, "channel": "1.1.0"}}),
    }


@pytest.mark.parametrize("min_mfv,max_mfv", [("1.0.1", "1.0.1"), ("0.9.9", "0.9.9")])
def test_get_latest_firmware__returns_correct_response__if_no_compatible_channel_firmware_files_found(
    min_mfv, max_mfv, mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_file_names = ["1_0_0.bin", "1_0_1.bin", "1_1_0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            {"max-software-version": "1.0.0", "min-software-version": "1.0.0"}
            if Bucket == expected_main_bucket_name
            else {"max-main-firmware-version": max_mfv, "min-main-firmware-version": min_mfv}
        )
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_versions": {"main": "1.1.0", "channel": None}}),
    }


def test_get_latest_firmware__returns_correct_response__when_multiple_compatible_firmware_files_found(
    mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

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
    test_main_firmware_versions = {
        "0_9_9.bin": {"min-main-firmware-version": "0.0.0", "max-main-firmware-version": "0.0.0"},
        "1_0_0.bin": {"min-main-firmware-version": "0.9.9", "max-main-firmware-version": "1.0.0"},
        "1_0_1.bin": {"min-main-firmware-version": "1.0.0", "max-main-firmware-version": "1.0.1"},
        "1_1_0.bin": {"min-main-firmware-version": "2.0.0", "max-main-firmware-version": "2.0.0"},
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            test_software_versions[Key]
            if Bucket == expected_main_bucket_name
            else test_main_firmware_versions[Key]
        )
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_versions": {"main": "1.0.1", "channel": "1.0.1"}}),
    }


def test_get_latest_firmware__returns_correct_response__when_multiple_compatible_main_firmware_files_found__with_no_max_software_version(
    mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

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
    test_main_firmware_versions = {
        "0_9_9.bin": {"min-main-firmware-version": "0.0.0", "max-main-firmware-version": "0.0.0"},
        "1_0_0.bin": {"min-main-firmware-version": "0.9.9", "max-main-firmware-version": "1.0.0"},
        "1_0_1.bin": {"min-main-firmware-version": "1.0.0"},
        "1_1_0.bin": {"min-main-firmware-version": "2.0.0"},
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            test_software_versions[Key]
            if Bucket == expected_main_bucket_name
            else test_main_firmware_versions[Key]
        )
    }

    test_event = {"queryStringParameters": {"software_version": "1.0.0", "main_firmware_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_firmware_versions": {"main": "1.0.1", "channel": "1.0.1"}}),
    }

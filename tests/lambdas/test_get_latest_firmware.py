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
def test_get_latest_firmware__returns_error_code_if_hardware_version_not_given(test_event):
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing hardware_version param"}),
    }


@pytest.mark.parametrize("test_event", [{}, {"queryStringParameters": None}, {"queryStringParameters": {}}])
def test_get_latest_firmware__logs_exception_if_software_version_not_given(test_event, mocker):
    spied_logger_exception = mocker.spy(get_latest_firmware.logger, "exception")
    get_latest_firmware.handler(test_event, None)
    spied_logger_exception.assert_called_once_with("Request missing hardware_version param")


def test_get_latest_firmware__gets_firmware_file_objects_from_s3_correctly(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    expected_main_bucket_name = "main_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    # mock to avoid errors
    mocker.patch.object(get_latest_firmware, "resolve_versions", autospec=True, return_value={})

    test_event = {"queryStringParameters": {"hardware_version": "0.0.0"}}
    get_latest_firmware.handler(test_event, None)

    assert mocked_s3_client.list_objects.call_count == 3
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

    expected_valid_main_file_names = ["0.0.0.bin", "99.99.99.bin"]
    expected_valid_channel_file_names = ["0.9.9.bin", "99.88.0.bin"]

    def lo_se(Bucket):
        test_file_names = [
            "x1.0.0.bin",
            "x.0.0.bin",
            "1.x.0.bin",
            "1.0.x.bin",
            "1.0.0,bin",
            "1.0.0.bit",
            "1.0.0.binx",
        ]
        if Bucket == expected_main_bucket_name:
            test_file_names.extend(expected_valid_main_file_names)
        else:
            test_file_names.extend(expected_valid_channel_file_names)
        return {"Contents": [{"Key": file_name} for file_name in test_file_names]}

    mocked_s3_client.list_objects.side_effect = lo_se
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            {"sw-version": "0.0.0"}
            if Bucket == expected_main_bucket_name
            else {"main-fw-version": "0.0.0", "hw-version": "0.0.0"}
        )
    }

    # mock to avoid errors
    mocker.patch.object(get_latest_firmware, "resolve_versions", autospec=True, return_value={})

    test_event = {"queryStringParameters": {"hardware_version": "0.0.0"}}
    get_latest_firmware.handler(test_event, None)

    expected_calls = [
        mocker.call(Bucket=expected_channel_bucket_name, Key=file_name)
        for file_name in expected_valid_channel_file_names
    ] * 2
    expected_calls.extend(
        [
            mocker.call(Bucket=expected_main_bucket_name, Key=file_name)
            for file_name in expected_valid_main_file_names
        ]
    )
    assert mocked_s3_client.head_object.call_args_list == expected_calls


def test_get_latest_firmware__logs_info__if_no_compatible_firmware_files_found(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client
    mocked_s3_client.list_objects.return_value = {"Contents": []}

    spied_logger_info = mocker.spy(get_latest_firmware.logger, "info")

    test_event = {"queryStringParameters": {"hardware_version": "1.0.0"}}
    get_latest_firmware.handler(test_event, None)
    spied_logger_info.assert_any_call("No compatible versions found")


def test_get_latest_firmware__returns_correct_response__if_dependency_mapping_fails(
    mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_file_names = ["1.0.0.bin", "1.0.1.bin", "1.1.0.bin"]
    mocked_s3_client.list_objects.return_value = {
        "Contents": [{"Key": file_name} for file_name in test_file_names]
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            {"sw-version": "0.0.0"}
            if Bucket == expected_main_bucket_name
            else {"main-fw-version": "0.0.0", "hw-version": "0.0.0"}
        )
    }

    mocker.patch.object(get_latest_firmware, "resolve_versions", autospec=True, side_effect=Exception)

    test_event = {"queryStringParameters": {"hardware_version": "1.0.0"}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"latest_versions": None}),
    }


@pytest.mark.parametrize(
    "hw_version,channel_fw_version,main_fw_version,sw_version",
    [
        ("1.0.0", "3.0.0", "3.0.0", "2.0.0"),
        ("2.0.0", "4.0.0", "4.0.0", "2.0.0"),
        ("3.0.0", "5.0.0", "6.0.0", "5.0.0"),
    ],
)
def test_get_latest_firmware__returns_correct_response__with_multiple_files_of_both_types_present(
    hw_version, channel_fw_version, main_fw_version, sw_version, mocked_boto3_client, mocker
):
    mocked_s3_client = mocked_boto3_client

    expected_main_bucket_name = "test_main_bucket"
    mocker.patch.object(get_latest_firmware, "S3_MAIN_BUCKET", expected_main_bucket_name)
    expected_channel_bucket_name = "channel_test_bucket"
    mocker.patch.object(get_latest_firmware, "S3_CHANNEL_BUCKET", expected_channel_bucket_name)

    test_main_file_names = [f"{version}.0.0.bin" for version in range(1, 7)]
    test_channel_file_names = [f"{version}.0.0.bin" for version in range(1, 6)]

    def se(Bucket):
        test_file_names = (
            test_main_file_names if Bucket == expected_main_bucket_name else test_channel_file_names
        )
        return {"Contents": [{"Key": file_name} for file_name in test_file_names]}

    mocked_s3_client.list_objects.side_effect = se

    test_channel_fw_metadata = {
        "1.0.0.bin": {"hw-version": "1.0.0", "main-fw-version": "1.0.0"},
        "2.0.0.bin": {"hw-version": "1.0.0", "main-fw-version": "2.0.0"},
        "3.0.0.bin": {"hw-version": "1.0.0", "main-fw-version": "3.0.0"},
        "4.0.0.bin": {"hw-version": "2.0.0", "main-fw-version": "4.0.0"},
        "5.0.0.bin": {"hw-version": "3.0.0", "main-fw-version": "6.0.0"},
    }
    test_main_fw_metadata = {
        "1.0.0.bin": {"sw-version": "1.0.0"},
        "2.0.0.bin": {"sw-version": "2.0.0"},
        "3.0.0.bin": {"sw-version": "2.0.0"},
        "4.0.0.bin": {"sw-version": "2.0.0"},
        "5.0.0.bin": {"sw-version": "3.0.0"},
        "6.0.0.bin": {"sw-version": "5.0.0"},
    }
    mocked_s3_client.head_object.side_effect = lambda Bucket, Key: {
        "Metadata": (
            test_main_fw_metadata[Key]
            if Bucket == expected_main_bucket_name
            else test_channel_fw_metadata[Key]
        )
    }

    test_event = {"queryStringParameters": {"hardware_version": hw_version}}
    response = get_latest_firmware.handler(test_event, None)
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "latest_versions": {
                    "sw": sw_version,
                    "main-fw": main_fw_version,
                    "channel-fw": channel_fw_version,
                }
            }
        ),
    }

import base64
import copy
import hashlib
import json

from botocore.exceptions import ClientError
import pytest

from ..test_utils import import_lambda

sdk_analysis = import_lambda("sdk_analysis", mock_imports=["curibio.sdk", "pymysql", "pandas"])

TEST_BUCKET_NAME = "test_name"
TEST_OBJECT_KEY = "customer_id/username/test_key"
TEST_RECORD = {"s3": {"bucket": {"name": TEST_BUCKET_NAME}, "object": {"key": TEST_OBJECT_KEY}}}
TEST_FILENAME = TEST_OBJECT_KEY.rsplit("/", 1)[1]


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_sqs_client = mocker.Mock()
    mocked_ssm_client = mocker.Mock()
    mocked_s3_client = mocker.Mock()
    mocked_ec2_client = mocker.Mock()

    mocked_s3_client.head_object.return_value = {"Metadata": {"upload-id": "test-id"}}

    mocked_dynamodb_client = mocker.Mock()

    def se(client_type):
        if client_type == "sqs":
            return mocked_sqs_client
        if client_type == "s3":
            return mocked_s3_client
        if client_type == "dynamodb":
            return mocked_dynamodb_client
        if client_type == "secretsmanager":
            return mocked_ssm_client
        if client_type == "ec2":
            return mocked_ec2_client

    mocker.patch.object(sdk_analysis.boto3, "client", autospec=True, side_effect=se)

    yield {
        "sqs": mocked_sqs_client,
        "s3": mocked_s3_client,
        "dynamodb": mocked_dynamodb_client,
        "secretsmanager": mocked_ssm_client,
        "ec2": mocked_ec2_client,
    }


def test_sdk_analysis__logs_exception_when_receiving_message_from_sqs_fails(mocker, mocked_boto3_client):
    mocked_sqs_client = mocked_boto3_client["sqs"]

    expected_error = ClientError({}, "")
    mocked_sqs_client.receive_message.side_effect = expected_error

    spied_logger_exception = mocker.spy(sdk_analysis.logger, "exception")
    sdk_analysis.handler(max_num_loops=1)
    spied_logger_exception.assert_called_once_with(f"receive_message failed. Error: {expected_error}")


def test_sdk_analysis__sleeps_after_each_loop_but_not_in_final_loop(mocker, mocked_boto3_client):
    mocked_sqs_client = mocked_boto3_client["sqs"]

    mocked_sleep = mocker.patch.object(sdk_analysis, "sleep", autospec=True)
    # Tanner (9/23/21): mocking receive_message to have error raised here in order to avoid mocking multiple other objects
    mocked_sqs_client.receive_message.side_effect = ClientError({}, "")

    sdk_analysis.handler(max_num_loops=2)
    mocked_sleep.assert_called_once_with(5)


def test_sdk_analysis__gets_messages_from_sqs_queue_correctly(mocker, mocked_boto3_client):
    mocked_sqs_client = mocked_boto3_client["sqs"]
    mocked_sqs_client.receive_message.return_value = {}

    expected_sqs_url = "test_url"
    mocker.patch.object(sdk_analysis, "SQS_URL", expected_sqs_url)

    sdk_analysis.handler(max_num_loops=1)
    mocked_sqs_client.receive_message.assert_called_once_with(
        QueueUrl=expected_sqs_url, MaxNumberOfMessages=1, WaitTimeSeconds=10
    )


def test_sdk_analysis__deletes_messages_from_sqs_queue_after_processing_them(mocker, mocked_boto3_client):
    mocked_sqs_client = mocked_boto3_client["sqs"]

    expected_sqs_url = "test_url"
    mocker.patch.object(sdk_analysis, "SQS_URL", expected_sqs_url)

    test_message = {"ReceiptHandle": "rh"}
    test_message_list = [test_message] * 3
    mocked_sqs_client.receive_message.return_value = {"Messages": test_message_list}

    sdk_analysis.handler(max_num_loops=1)
    assert mocked_sqs_client.delete_message.call_count == len(test_message_list)
    mocked_sqs_client.delete_message.called_with(
        QueueUrl=expected_sqs_url, ReceiptHandle=test_message["ReceiptHandle"]
    )


@pytest.mark.parametrize(
    "test_message",
    [
        {},
        {"Body": json.dumps({})},
        {"Body": json.dumps({"other_key": "val"})},
        {"Body": json.dumps({"Records": []})},
        {"Body": json.dumps({"Records": [{}]})},
        {"Body": json.dumps({"Records": [{"eventSource": "aws:s3"}]})},
        {"Body": json.dumps({"Records": [{"eventName": "ObjectCreated:Post"}]})},
    ],
)
def test_sdk_analysis__does_not_process_message_or_record_from_sqs_queue_that_is_not_formatted_correctly(
    test_message, mocker, mocked_boto3_client
):
    mocked_sqs_client = mocked_boto3_client["sqs"]

    test_message.update({"ReceiptHandle": "rh"})
    mocked_sqs_client.receive_message.return_value = {"Messages": [test_message]}
    spied_process_record = mocker.spy(sdk_analysis, "process_record")

    sdk_analysis.handler(max_num_loops=1)
    spied_process_record.assert_not_called()


def test_sdk_analysis__processes_each_record_of_each_record_of_each_message_from_sqs_queue(
    mocker, mocked_boto3_client
):
    mocked_sqs_client = mocked_boto3_client["sqs"]
    mocked_s3_client = mocked_boto3_client["s3"]
    mocked_dynamodb_client = mocked_boto3_client["dynamodb"]

    test_num_records = 5
    test_records = [
        {"eventSource": "aws:s3", "eventName": "ObjectCreated:Post", "num": i}
        for i in range(test_num_records)
    ]
    test_messages = [
        {"Body": json.dumps({"Records": records}), "ReceiptHandle": "rh"}
        for records in (test_records[:2], test_records[2:])
    ]

    mocked_sqs_client.receive_message.return_value = {"Messages": test_messages}
    mocked_process_record = mocker.patch.object(sdk_analysis, "process_record")

    sdk_analysis.handler(max_num_loops=1)
    assert mocked_process_record.call_count == test_num_records
    for record in test_records:
        mocked_process_record.assert_any_call(record, mocked_s3_client, mocked_dynamodb_client)


def test_sdk_analysis__handles_info_logging_pertaining_to_sqs_queue(mocker, mocked_boto3_client):
    mocked_sqs_client = mocked_boto3_client["sqs"]

    test_message_list = []
    mocked_sqs_client.receive_message.return_value = {"Messages": test_message_list}

    expected_sqs_url = "test_url"
    mocker.patch.object(sdk_analysis, "SQS_URL", expected_sqs_url)
    spied_logger_info = mocker.spy(sdk_analysis.logger, "info")

    sdk_analysis.handler(max_num_loops=1)
    spied_logger_info.assert_any_call(f"Receiving messages on {expected_sqs_url}")
    spied_logger_info.assert_any_call(f"Received: {len(test_message_list)}")
    spied_logger_info.assert_any_call("Received: 0")


def test_process_record__retrieves_metadata_of_file_correctly(mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client["s3"]

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    mocked_s3_client.head_object.assert_called_once_with(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY)


def test_process_record__logs_error_when_one_is_raised_while_retrieving_metadata_from_s3_and_does_not_attempt_to_download_the_file(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client["s3"]

    expected_error = ClientError({}, "")
    mocked_s3_client.head_object.side_effect = expected_error
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    spied_logger_error.assert_called_once_with(
        f"Error occurred while retrieving head object of {TEST_BUCKET_NAME}/{TEST_OBJECT_KEY}: {expected_error}"
    )
    mocked_s3_client.download_file.assert_not_called()


def test_process_record__correctly_downloads_file_to_temporary_directory(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client["s3"]

    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    spied_temporary_dir.assert_called_once_with(dir="/tmp")
    mocked_s3_client.download_file.assert_called_once_with(
        TEST_BUCKET_NAME, TEST_OBJECT_KEY, f"{spied_temporary_dir.spy_return.name}/{TEST_FILENAME}"
    )


def test_process_record__handles_error_raised_while_downloading_file_from_s3(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client["s3"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]

    expected_error = ClientError({}, "")
    mocked_s3_client.download_file.side_effect = expected_error
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")
    spied_update_status = mocker.spy(sdk_analysis, "update_sdk_status")
    spied_pr_from_dir = mocker.spy(sdk_analysis.PlateRecording, "from_directory")

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    spied_logger_error.assert_called_once_with(
        f"Failed to download {TEST_BUCKET_NAME}/{TEST_OBJECT_KEY}: {expected_error}"
    )
    spied_update_status.assert_called_once_with(
        mocked_boto3_client["dynamodb"], expected_upload_id, "error accessing file"
    )
    spied_pr_from_dir.assert_not_called()


def test_process_record__sets_file_status_to_analysis_running_then_runs_sdk_analysis_on_file(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client["s3"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]

    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")
    mocked_pr_from_dir = mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)

    error_tracker = {"funcs_called_out_of_order": False}

    def se(*args):
        if args[-1] == "analysis running":
            error_tracker["funcs_called_out_of_order"] = mocked_pr_from_dir.call_count != 0

    mocked_update_status = mocker.patch.object(
        sdk_analysis, "update_sdk_status", autospec=True, side_effect=se
    )

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    assert error_tracker["funcs_called_out_of_order"] is False
    assert mocked_update_status.call_args_list[0] == mocker.call(
        mocked_boto3_client["dynamodb"], expected_upload_id, "analysis running"
    )
    mocked_pr_from_dir.assert_called_once_with(spied_temporary_dir.spy_return)
    mocked_pr_from_dir.return_value.write_xlsx.assert_called_once_with(
        spied_temporary_dir.spy_return.name, file_name=f"{TEST_FILENAME}.xlsx"
    )


def test_process_record__handles_error_raised_while_running_sdk_analysis(mocker, mocked_boto3_client):
    expected_upload_id = mocked_boto3_client["s3"].head_object.return_value["Metadata"]["upload-id"]

    expected_error = Exception("test_exception")
    mocked_pr_from_dir = mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    mocked_pr_from_dir.return_value.write_xlsx.side_effect = expected_error

    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")
    mocked_update_status = mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)

    sdk_analysis.process_record(
        copy.deepcopy(TEST_RECORD), mocked_boto3_client["s3"], mocked_boto3_client["dynamodb"]
    )
    spied_logger_error.assert_called_once_with(f"SDK analysis failed: {expected_error}")
    mocked_update_status.assert_called_with(
        mocked_boto3_client["dynamodb"], expected_upload_id, "error during analysis"
    )


def test_process_record__uploads_file_created_by_sdk_analysis_to_s3_bucket_correctly_and_sets_file_status_to_analysis_complete(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client["s3"]
    mocked_dynamo_client = mocked_boto3_client["dynamodb"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]

    expected_upload_bucket = "test_url"
    mocker.patch.object(hashlib, "md5")
    mocked_base64 = mocker.patch.object(base64, "b64encode")
    expected_md5 = mocked_base64().decode()
    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)

    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")
    mocked_open = mocker.patch("builtins.open", autospec=True)

    mocked_update_status = mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    mocker.patch.object(sdk_analysis.main, "handle_db_metadata_insertions", autospec=True)

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    expected_dir_name = spied_temporary_dir.spy_return.name
    mocked_open.assert_called_with(f"{expected_dir_name}/{TEST_FILENAME}.xlsx", "rb")
    mocked_s3_client.put_object.assert_called_once_with(
        Body=mocked_open.return_value.__enter__(),
        Bucket=expected_upload_bucket,
        Key=f"{TEST_OBJECT_KEY}.xlsx",
        ContentMD5=expected_md5,
    )
    assert mocked_update_status.call_args_list[1] == mocker.call(
        mocked_dynamo_client, expected_upload_id, "analysis complete"
    )


def test_process_record__handles_error_raised_while_uploading_file_to_s3(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client["s3"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]
    mocker.patch.object(hashlib, "md5")
    mocker.patch.object(base64, "b64encode")
    expected_error = Exception("test_exception")
    mocked_s3_client.put_object.side_effect = expected_error

    expected_upload_bucket = "test_url"
    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)

    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")
    mocker.patch("builtins.open", autospec=True)
    mocked_update_status = mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")
    mocked_db_handling = mocker.patch.object(
        sdk_analysis.main, "handle_db_metadata_insertions", autospec=True
    )

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    expected_dir_name = spied_temporary_dir.spy_return.name
    expected_file_name = f"{TEST_FILENAME}.xlsx"
    spied_logger_error.assert_called_with(
        f"S3 Upload failed for {expected_dir_name}/{expected_file_name} to {expected_upload_bucket}/{TEST_OBJECT_KEY}.xlsx: {expected_error}"
    )

    mocked_update_status.assert_called_with(
        mocked_boto3_client["dynamodb"], expected_upload_id, "error during upload of analyzed file"
    )
    mocked_db_handling.assert_not_called()


def test_process_record__after_successful_upload_logger_handles_failed_aurora_db_insertion(
    mocker, mocked_boto3_client
):
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")
    mocked_s3_client = mocked_boto3_client["s3"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]
    mocker.patch.object(hashlib, "md5")
    mocker.patch.object(base64, "b64encode")

    expected_upload_bucket = "test_url"
    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)

    mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")
    mocker.patch("builtins.open", autospec=True)
    mocked_update_status = mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocker.patch.object(sdk_analysis.main, "handle_db_metadata_insertions", side_effect=Exception("ERROR"))

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])

    mocked_update_status.assert_called_with(
        mocked_boto3_client["dynamodb"], expected_upload_id, "error inserting analysis to database"
    )

    spied_logger_error.assert_called_with("Recording metadata failed to store in aurora database: ERROR")


def test_process_record__after_successful_upload_logger_handles_successful_aurora_db_insertion(
    mocker, mocked_boto3_client
):
    spied_logger_info = mocker.spy(sdk_analysis.logger, "info")
    mocked_s3_client = mocked_boto3_client["s3"]
    expected_upload_id = mocked_s3_client.head_object.return_value["Metadata"]["upload-id"]

    expected_upload_bucket = "test_bucket"
    expected_db_cluster_endpoint = "test_host"
    expected_file_name = f"{TEST_OBJECT_KEY}.xlsx"

    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)
    mocker.patch.object(sdk_analysis, "DB_CLUSTER_ENDPOINT", expected_db_cluster_endpoint)
    mocker.patch.object(hashlib, "md5")
    mocked_base64 = mocker.patch.object(base64, "b64encode")
    expected_md5 = mocked_base64().decode()

    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")
    mocked_open = mocker.patch("builtins.open", autospec=True)
    mocked_update_status = mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocked_PR_instance = mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    mocked_db_handling = mocker.patch.object(
        sdk_analysis.main, "handle_db_metadata_insertions", autospec=True
    )
    mocker.patch.object(mocked_s3_client, "put_object")

    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])
    expected_dir_name = spied_temporary_dir.spy_return.name

    mocked_update_status.assert_any_call(
        mocked_boto3_client["dynamodb"], expected_upload_id, "analysis successfully inserted into database"
    )
    spied_logger_info.assert_any_call(
        f"Inserting {expected_dir_name}/{TEST_FILENAME}.xlsx metadata into aurora database"
    )

    test_args = [mocked_open.return_value.__enter__(), mocked_PR_instance.return_value, expected_md5]
    mocked_db_handling.assert_called_with(
        expected_upload_bucket, expected_file_name, expected_db_cluster_endpoint, test_args
    )


def test_set_info_dict__correctly_retrieves_aws_credentials(mocker, mocked_boto3_client):
    mocked_s3_client = mocked_boto3_client["s3"]

    expected_upload_bucket = "test_url"
    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)
    mocker.patch.object(hashlib, "md5")
    mocker.patch.object(base64, "b64encode")

    mocker.patch.object(sdk_analysis.main, "get_ssm_secrets", return_value=("test_username", "test_password"))

    mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocker.patch("builtins.open", autospec=True)
    mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])

    expected_info_dict = {
        "db_name": "mantarray_recordings",
        "db_password": "test_password",
        "db_username": "test_username",
    }
    assert sdk_analysis.main.INFO_DICT == expected_info_dict


def test_load_data_into_dataframe__successfully_gets_called_after_successful_db_connection(
    mocker, mocked_boto3_client
):
    mocked_s3_client = mocked_boto3_client["s3"]
    mocker.patch.object(hashlib, "md5")
    mocker.patch.object(base64, "b64encode")
    mocker.patch.object(sdk_analysis.main, "get_ssm_secrets", return_value=("test_username", "test_password"))

    expected_db_cluster_endpoint = "test_host"
    expected_upload_bucket = "test_url"
    mocker.patch.object(sdk_analysis, "S3_UPLOAD_BUCKET", expected_upload_bucket)
    mocker.patch.object(sdk_analysis, "DB_CLUSTER_ENDPOINT", expected_db_cluster_endpoint)

    mocker.patch.object(sdk_analysis.main.pymysql, "connect")
    format_spy = mocker.patch.object(sdk_analysis.main, "load_data_to_dataframe")

    mocked_open = mocker.patch("builtins.open", autospec=True)
    mocker.patch.object(sdk_analysis, "update_sdk_status", autospec=True)
    mocker.patch.object(mocked_s3_client, "put_object", autospec=True)
    mocked_PR_instance = mocker.patch.object(sdk_analysis.PlateRecording, "from_directory", autospec=True)
    sdk_analysis.process_record(copy.deepcopy(TEST_RECORD), mocked_s3_client, mocked_boto3_client["dynamodb"])

    format_spy.assert_any_call(mocked_open.return_value.__enter__(), mocked_PR_instance.return_value)


def test_process_record__handles_info_logging(mocker, mocked_boto3_client):
    spied_logger_info = mocker.spy(sdk_analysis.logger, "info")
    spied_temporary_dir = mocker.spy(sdk_analysis.tempfile, "TemporaryDirectory")

    sdk_analysis.process_record(
        copy.deepcopy(TEST_RECORD), mocked_boto3_client["s3"], mocked_boto3_client["dynamodb"]
    )
    spied_logger_info.assert_any_call(f"Retrieving Head Object of {TEST_BUCKET_NAME}/{TEST_OBJECT_KEY}")
    spied_logger_info.assert_any_call(
        f"Download {TEST_BUCKET_NAME}/{TEST_OBJECT_KEY} to {spied_temporary_dir.spy_return.name}/{TEST_FILENAME}"
    )


def test_update_sdk_status__updates_item_correctly(mocker, mocked_boto3_client):
    mocked_dynamodb_client = mocked_boto3_client["dynamodb"]

    expected_table_name = "test_table"
    mocker.patch.object(sdk_analysis, "SDK_STATUS_TABLE", expected_table_name)

    test_upload_id = "test_id"
    test_status = "test_status"
    sdk_analysis.update_sdk_status(mocked_dynamodb_client, test_upload_id, test_status)
    mocked_dynamodb_client.update_item.assert_called_once_with(
        TableName=expected_table_name,
        Key={"upload_id": {"S": test_upload_id}},
        UpdateExpression="SET sdk_status = :val",
        ExpressionAttributeValues={":val": {"S": test_status}},
        ConditionExpression="attribute_exists(upload_id)",
    )


def test_update_sdk_status__handles_conditional_check_failed_exceptions_raised_from_updating_item(
    mocker, mocked_boto3_client
):
    mocked_dynamodb_client = mocked_boto3_client["dynamodb"]

    expected_error = ClientError({"Error": {"Code": "ConditionalCheckFailedException"}}, "")
    mocked_dynamodb_client.update_item.side_effect = expected_error

    expected_table_name = "test_table"
    mocker.patch.object(sdk_analysis, "SDK_STATUS_TABLE", expected_table_name)
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")

    test_upload_id = "test_id"
    test_status = "test_status"
    sdk_analysis.update_sdk_status(mocked_dynamodb_client, test_upload_id, test_status)
    spied_logger_error.assert_any_call(f"Error: {expected_error}")
    spied_logger_error.assert_any_call(
        f"Upload ID: {test_upload_id} was not found in table {expected_table_name}"
    )
    mocked_dynamodb_client.put_item.assert_called_once_with(
        TableName=expected_table_name,
        Item={"upload_id": {"S": test_upload_id}, "sdk_status": {"S": test_status}},
    )


def test_update_sdk_status__logs_other_aws_errors_raised_from_updating_item(mocker, mocked_boto3_client):
    mocked_dynamodb_client = mocked_boto3_client["dynamodb"]

    expected_error = ClientError({"Error": {"Code": "SomeOtherException"}}, "")
    mocked_dynamodb_client.update_item.side_effect = expected_error

    expected_table_name = "test_table"
    mocker.patch.object(sdk_analysis, "SDK_STATUS_TABLE", expected_table_name)
    spied_logger_error = mocker.spy(sdk_analysis.logger, "error")

    test_upload_id = "test_id"
    test_status = "test_status"
    sdk_analysis.update_sdk_status(mocked_dynamodb_client, test_upload_id, test_status)
    spied_logger_error.assert_called_once_with(f"Error: {expected_error}")
    mocked_dynamodb_client.put_item.assert_not_called()

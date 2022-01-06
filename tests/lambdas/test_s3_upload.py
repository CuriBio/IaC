import json

from botocore.exceptions import ClientError
import pytest

from ..test_utils import import_lambda

s3_upload = import_lambda("s3_upload")


@pytest.fixture(scope="function", name="mocked_boto3_client")
def fixture_mocked_boto3_client(mocker):
    mocked_s3_client = mocker.Mock()
    mocked_s3_client.generate_presigned_post.return_value = None

    mocked_dynamodb_client = mocker.Mock()

    def se(client_type):
        if client_type == "s3":
            return mocked_s3_client
        if client_type == "dynamodb":
            return mocked_dynamodb_client

    mocker.patch.object(s3_upload.boto3, "client", autospec=True, side_effect=se)

    yield mocked_s3_client, mocked_dynamodb_client


def test_s3_upload__returns_error_code_if_file_name_not_given():
    response = s3_upload.handler(
        {"body": json.dumps({"upload_type": "sdk"}), "headers": {"Content-MD5": ""}}, None
    )
    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing file_name"}),
    }


def test_s3_upload__logs_exception_if_file_name_not_given(mocker):
    spied_logger_exception = mocker.spy(s3_upload.logger, "exception")
    s3_upload.handler({"body": json.dumps({"upload_type": "sdk"})}, None)
    spied_logger_exception.assert_called_once_with("file_name not found in request body")


def test_s3_upload__logs_exception_if_content_md5_header_is_not_present(mocker):
    spied_logger_exception = mocker.spy(s3_upload.logger, "exception")
    response = s3_upload.handler({"body": json.dumps({"file_name": "", "upload_type": "sdk"})}, None)
    spied_logger_exception.assert_called_once_with("Content-MD5 header not found in request")

    assert response == {
        "statusCode": 400,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"message": "Missing Content-MD5 header"}),
    }


def test_s3_upload__calls_generate_presigned_post_with_correct_values(mocker, mocked_boto3_client):
    mocked_s3_client, _ = mocked_boto3_client

    expected_bucket_name = "test_bucket"
    mocker.patch.object(s3_upload, "SDK_UPLOAD_BUCKET", expected_bucket_name)
    spied_uuid4 = mocker.spy(s3_upload.uuid, "uuid4")

    test_file_name = "test_file"
    s3_upload.handler(
        {
            "body": json.dumps({"file_name": test_file_name, "upload_type": "sdk"}),
            "headers": {"Content-MD5": ""},
        },
        None,
    )

    expected_upload_id = str(spied_uuid4.spy_return)
    expected_fields = {"x-amz-meta-upload-id": expected_upload_id, "Content-MD5": ""}
    expected_conditions = [{"x-amz-meta-upload-id": expected_upload_id}, ["starts-with", "$Content-MD5", ""]]
    mocked_s3_client.generate_presigned_post.assert_called_once_with(
        expected_bucket_name,
        test_file_name,
        Fields=expected_fields,
        Conditions=expected_conditions,
        ExpiresIn=3600,
    )


def test_s3_upload__handles_info_logging(mocker, mocked_boto3_client):
    mocked_s3_client, _ = mocked_boto3_client

    expected_params = {"param1": 1, "param2": "val"}
    mocked_s3_client.generate_presigned_post.return_value = expected_params
    spied_logger_info = mocker.spy(s3_upload.logger, "info")

    test_file_name = "test_file"
    test_event = {
        "body": json.dumps({"file_name": test_file_name, "upload_type": "sdk"}),
        "headers": {"Content-MD5": ""},
    }
    s3_upload.handler(test_event, None)
    spied_logger_info.assert_any_call(f"event: {test_event}")
    spied_logger_info.assert_any_call(f"Got presigned URL params for an sdk upload: {expected_params}")


def test_s3_upload__returns_correct_response_for_a_given_file_name(mocker, mocked_boto3_client):
    mocked_s3_client, _ = mocked_boto3_client

    expected_params = {"param1": 1, "param2": "val"}
    mocked_s3_client.generate_presigned_post.return_value = expected_params
    spied_uuid4 = mocker.spy(s3_upload.uuid, "uuid4")

    test_file_name = "test_file"
    response = s3_upload.handler(
        {
            "body": json.dumps({"file_name": test_file_name, "upload_type": "sdk"}),
            "headers": {"Content-MD5": ""},
        },
        None,
    )
    assert response == {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"presigned_params": expected_params, "upload_id": str(spied_uuid4.spy_return)}),
    }


def test_s3_upload__puts_item_into_dynamodb_table_correctly(mocker, mocked_boto3_client):
    _, mocked_dynamodb_client = mocked_boto3_client

    expected_table_name = "test_table"
    mocker.patch.object(s3_upload, "SDK_STATUS_TABLE", expected_table_name)
    spied_uuid4 = mocker.spy(s3_upload.uuid, "uuid4")

    test_file_name = "test_file"
    s3_upload.handler(
        {
            "body": json.dumps({"file_name": test_file_name, "upload_type": "sdk"}),
            "headers": {"Content-MD5": ""},
        },
        None,
    )
    mocked_dynamodb_client.put_item.assert_called_once_with(
        TableName=expected_table_name,
        Item={"upload_id": {"S": str(spied_uuid4.spy_return)}, "sdk_status": {"S": "analysis pending"}},
        ConditionExpression="attribute_not_exists(upload_id)",
    )


def test_s3_upload__logs_exception_when_generate_presigned_post_raises_ClientError(
    mocker, mocked_boto3_client
):
    mocked_s3_client, _ = mocked_boto3_client

    mocked_s3_client.generate_presigned_post.side_effect = ClientError({}, "")
    spied_logger_exception = mocker.spy(s3_upload.logger, "exception")

    with pytest.raises(ClientError):
        s3_upload.handler(
            {"body": json.dumps({"file_name": "", "upload_type": "sdk"}), "headers": {"Content-MD5": ""}},
            None,
        )
    spied_logger_exception.assert_called_once_with("Couldn't get presigned URL params for an sdk upload")


def test_s3_upload__errors_if_content_md5_header_is_not_valid_format(mocked_boto3_client):
    mocked_s3_client, _ = mocked_boto3_client

    expected_params = {"param1": 1, "param2": "val", "Content-MD5": b"1B2M2Y8AsgTpgAmY7PhCfg=="}
    mocked_s3_client.generate_presigned_post.return_value = expected_params

    with pytest.raises(TypeError):
        response = s3_upload.handler(
            {
                "body": json.dumps({"file_name": "", "upload_type": "sdk"}),
                "headers": {"Content-MD5": b"1B2M2Y8AsgTpgAmY7PhCfg=="},
            },
            None,
        )
        assert response == "Object of type bytes is not JSON serializable"

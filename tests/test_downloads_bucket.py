# -*- coding: utf-8 -*-
from typing import Any
from typing import Dict
import uuid

import boto3
from mypy_boto3_sts import STSClient
import pytest
import requests


@pytest.fixture(scope="function", name="downloads_bucket_name")
def fixture_downloads_bucket_name(deployment_tier):
    suffix = ""
    if deployment_tier in ["test", "modl"]:
        suffix = f"-{deployment_tier}"
    return f"downloads.curibio{suffix}.com"


def _create_generic_object(
    sts_client: STSClient, account_id: str, downloads_bucket_name: str
) -> Dict[str, Any]:
    client = sts_client
    assumed_role_object = client.assume_role(
        RoleArn=f"arn:aws:iam::{account_id}:role/s3_downloads_role",
        RoleSessionName="a-role-session-name",
    )
    credentials = assumed_role_object["Credentials"]
    s3_resource = boto3.resource(
        "s3",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )
    bucket = s3_resource.Bucket(downloads_bucket_name)
    obj_key = f"tests/{uuid.uuid4()}"
    obj_contents = str(uuid.uuid4())

    created_object = bucket.put_object(Body=obj_contents, Key=obj_key)
    return {"object": created_object, "contents": obj_contents, "key": obj_key}


@pytest.fixture(scope="function", name="Given_an_object_is_in_the_downloads_bucket")
def fixture_Given_an_object_is_in_the_downloads_bucket(
    deployment_aws_account_id, downloads_bucket_name
):
    object_properties = _create_generic_object(
        boto3.client("sts"), deployment_aws_account_id, downloads_bucket_name
    )
    yield object_properties
    created_object = object_properties["object"]
    # since this is a versioned bucket, to completely delete the object, the version ID needs to be specified
    created_object.delete(VersionId=created_object.version_id)


def test_When_admin_account_assumes_marketing_role__Then_an_object_can_be_created_and_deleted_in_the_downloads_bucket(
    tf_workspace_name, deployment_tier, deployment_aws_account_id, downloads_bucket_name
):
    assert isinstance(tf_workspace_name, str)
    print(f"Workspace name in pytest: {tf_workspace_name}")  # allow-print
    print(f"Determined deployment tier: {deployment_tier}")  # allow-print
    client = boto3.client("sts")
    account_id = client.get_caller_identity()["Account"]
    # confirm that the client being used to create the object is the admin account
    assert account_id == "424924102580"
    object_properties = _create_generic_object(
        client, deployment_aws_account_id, downloads_bucket_name
    )
    created_object = object_properties["object"]
    expected_key = object_properties["key"]
    assert created_object.key == expected_key

    # since this is a versioned bucket, to completely delete the object, the version ID needs to be specified
    created_object.delete(VersionId=created_object.version_id)


def test_Given_an_object_is_in_the_downloads_bucket__When_a_generic_http_request_is_sent_for_the_object__Then_it_can_be_accessed_since_the_bucket_is_configured_for_public_access(
    downloads_bucket_name, Given_an_object_is_in_the_downloads_bucket
):
    object_properties = Given_an_object_is_in_the_downloads_bucket
    object_key = object_properties["object"].key
    url = f"https://{downloads_bucket_name}/{object_key}"
    r = requests.get(url)
    assert r.text == object_properties["contents"]

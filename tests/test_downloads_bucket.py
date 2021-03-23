# -*- coding: utf-8 -*-
import uuid

import boto3
import pytest


@pytest.fixture(scope="function", name="downloads_bucket_name")
def fixture_downloads_bucket_name(deployment_tier):
    suffix = ""
    if deployment_tier in ["test", "modl"]:
        suffix = f"-{deployment_tier}"
    return f"downloads.curibio{suffix}.com"


def test_When_admin_account_assumes_marketing_role__Then_an_object_can_be_created_and_deleted_in_the_downloads_bucket(
    tf_workspace_name, deployment_tier, deployment_aws_account_id, downloads_bucket_name
):
    assert isinstance(tf_workspace_name, str)
    print(f"Workspace name in pytest: {tf_workspace_name}")  # allow-print
    print(f"Determined deployment tier: {deployment_tier}")  # allow-print

    client = boto3.client("sts")
    assumed_role_object = client.assume_role(
        RoleArn=f"arn:aws:iam::{deployment_aws_account_id}:role/s3_downloads_role",
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
    assert created_object.key == obj_key

    # since this is a versioned bucket, to completely delete the object, the version ID needs to be specified
    created_object.delete(VersionId=created_object.version_id)

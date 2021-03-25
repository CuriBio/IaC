# -*- coding: utf-8 -*-
import os
from typing import Any
from typing import Dict
import uuid

import boto3
import hcl2
from mypy_boto3_sts import STSClient
import pytest
import requests

from .fixtures import PATH_TO_INFRA_DIR
from .test_dns import fixture_domain_name

__fixtures__ = (fixture_domain_name,)


@pytest.fixture(scope="function", name="downloads_bucket_name")
def fixture_downloads_bucket_name(domain_name) -> str:
    return f"downloads.{domain_name}"


def _create_generic_object(
    sts_client: STSClient, deployment_account_id: str, downloads_bucket_name: str
) -> Dict[str, Any]:
    with open(
        os.path.join(PATH_TO_INFRA_DIR, "modules", "curi", "s3_downloads", "iam.tf"),
        "r",
    ) as in_file:
        iam_tf_info = hcl2.load(in_file)
    role_name = next(iter(iam_tf_info["resource"][0]["aws_iam_role"].values()))["name"][
        0
    ]

    assumed_role_object = sts_client.assume_role(
        RoleArn=f"arn:aws:iam::{deployment_account_id}:role/{role_name}",
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


def When_admin_account_assumes_marketing_role__Then_an_object_can_be_created_and_deleted_in_the_downloads_bucket(
    tf_workspace_name, deployment_tier, deployment_aws_account_id, downloads_bucket_name
):
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


class Given_an_object_is_in_the_downloads_bucket:
    # pylint:disable=too-few-public-methods # Eli (3/23/21): trying out this style of having Given as a class wrapping tests that use something in common. Might in future just remove this pylint rule for test suites
    object_properties: Dict[str, Any]

    @pytest.fixture(
        autouse=True
    )  # adapted from https://stackoverflow.com/questions/21430900/py-test-skips-test-class-if-constructor-is-defined
    def _setup(self, deployment_aws_account_id, downloads_bucket_name):
        object_properties = _create_generic_object(
            boto3.client("sts"), deployment_aws_account_id, downloads_bucket_name
        )
        self.object_properties = object_properties
        created_object = object_properties["object"]
        yield object_properties
        # since this is a versioned bucket, to completely delete the object, the version ID needs to be specified
        created_object.delete(VersionId=created_object.version_id)

    def When_a_public_http_request_is_sent_for_the_object__Then_it_can_be_accessed(
        self, downloads_bucket_name
    ):
        object_properties = self.object_properties
        object_key = object_properties["object"].key
        url = f"https://{downloads_bucket_name}/{object_key}"
        r = requests.get(url)
        assert r.text == object_properties["contents"]

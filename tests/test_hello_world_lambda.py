# -*- coding: utf-8 -*-
import json
import logging
import os
import time

import botocore
import hcl2

from .fixtures import PATH_TO_INFRA_DIR

logger = logging.getLogger(__name__)


def _invoke_lambda(lambda_client, *args, **kwargs):
    try:
        return lambda_client.invoke(*args, **kwargs)
    except botocore.exceptions.ClientError as e:
        # Eli (3/26/21): Sporadic errors occuring in CI after a terraform apply. There doesn't appear to be standard documentation on how to handle this, so just trying to sleep and run it again
        # botocore.exceptions.ClientError: An error occurred (CodeArtifactUserPendingException) when calling the Invoke operation (reached max retries: 4): INFO: Lambda is initializing your function. It will be ready to invoke shortly.
        if "CodeArtifactUserPendingException" in str(e):
            logger.warning(
                "A CodeArtifactUserPendingException occurred, sleeping for 15 seconds and trying again: %s",
                e,
            )
            time.sleep(15)
            return lambda_client.invoke(*args, **kwargs)
        raise e


def When_the_function_is_invoked__Then_it_returns_the_expected_response_payload(
    deployment_tier, tf_workspace_name, deployment_aws_account_id, boto3_test_session
):
    with open(
        os.path.join(
            PATH_TO_INFRA_DIR, "environments", deployment_tier, "terraform.tfvars"
        ),
        "r",
    ) as in_file:
        tf_info = hcl2.load(in_file)
    lambda_function_name = tf_info["function_name"][0]
    lambda_function_name = f"{tf_workspace_name}-{lambda_function_name}"
    lambda_arn = f"arn:aws:lambda:us-east-1:{deployment_aws_account_id}:function:{lambda_function_name}"
    lambda_client = boto3_test_session.client("lambda", region_name="us-east-1")
    response = _invoke_lambda(
        lambda_client, FunctionName=lambda_arn, InvocationType="RequestResponse",
    )
    assert response["StatusCode"] == 200
    extracted_payload = json.loads(response["Payload"].read().decode("utf-8"))
    assert "Hello from" in extracted_payload

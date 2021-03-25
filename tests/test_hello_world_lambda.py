# -*- coding: utf-8 -*-
import os

import hcl2

from .fixtures import PATH_TO_INFRA_DIR


def When_the_function_is_invoked__Then_it_returns_a_response(
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
    response = lambda_client.invoke(
        FunctionName=lambda_arn, InvocationType="RequestResponse",
    )
    print(response)  # allow-print

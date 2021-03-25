# -*- coding: utf-8 -*-
"""Pytest configuration."""
import sys
from typing import List

from _pytest.config import Config
from _pytest.config.argparsing import Parser
from _pytest.python import Function
import boto3
import pytest

sys.dont_write_bytecode = True
sys.stdout = (
    sys.stderr
)  # allow printing of pytest output when running pytest-xdist https://stackoverflow.com/questions/27006884/pytest-xdist-without-capturing-output


def pytest_addoption(parser: Parser) -> None:
    parser.addoption(
        "--full-ci",
        action="store_true",
        default=False,
        help="run tests that are marked as only for CI",
    )
    parser.addoption(
        "--include-slow-tests",
        action="store_true",
        default=False,
        help="run tests that are a bit slow",
    )
    parser.addoption("--tf-workspace-name", action="store")


# adapted from https://stackoverflow.com/questions/40880259/how-to-pass-arguments-in-pytest-by-command-line
def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.tf_workspace_name
    if option_value is None:
        raise NotImplementedError(
            "A Terraform workspace name must be supplied as a command line argument when running pytest. Example: pytest --tf-workspace-name=modl"
        )
    if "tf_workspace_name" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("tf_workspace_name", [option_value])


def pytest_collection_modifyitems(config: Config, items: List[Function]) -> None:
    if not config.getoption("--full-ci"):
        skip_ci_only = pytest.mark.skip(
            reason="these tests are skipped unless --full-ci option is set"
        )
        for item in items:
            if "only_run_in_ci" in item.keywords:
                item.add_marker(skip_ci_only)

    if not config.getoption("--include-slow-tests"):
        skip_slow = pytest.mark.skip(
            reason="these tests are skipped unless --include-slow-tests option is set"
        )
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)


@pytest.fixture(
    scope="function",  # Eli (3/23/21): tried to set this as session or module scoped, but gave errors related to "factories", presumably related to the way the command line argument is processed for the Terraform workspace name
    name="deployment_tier",
)
def fixture_deployment_tier(tf_workspace_name) -> str:
    if tf_workspace_name in ["prod", "modl"]:
        return tf_workspace_name
    return "test"


@pytest.fixture(scope="function", name="deployment_aws_account_id")
def fixture_deployment_aws_account_id(deployment_tier):
    lookup = {"test": "077346344852", "modl": "725604423866", "prod": "245339368379"}
    return lookup[deployment_tier]


@pytest.fixture(scope="function", name="boto3_test_session")
def fixture_boto3_test_session(deployment_aws_account_id):
    client = boto3.client("sts")
    assumed_role_object = client.assume_role(
        RoleArn=f"arn:aws:iam::{deployment_aws_account_id}:role/iac_testing_role",
        RoleSessionName="a-role-session-name2",
    )
    credentials = assumed_role_object["Credentials"]
    session = boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name="us-east-1",
    )
    yield session

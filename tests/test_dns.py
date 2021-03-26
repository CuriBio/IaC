# -*- coding: utf-8 -*-
import time

import pytest
import requests


@pytest.fixture(scope="function", name="domain_name")
def fixture_domain_name(deployment_tier) -> str:
    suffix = ""
    if deployment_tier in ["test", "modl"]:
        suffix = f"-{deployment_tier}"
    return f"curibio{suffix}.com"


def When_an_http_request_is_made_to_company_homepage__Then_it_can_be_accessed(
    domain_name,
):
    url = f"https://{domain_name}"
    r = requests.get(url)
    assert r.status_code == 200
    assert "Curi Bio" in r.text
    time.sleep(
        1
    )  # Eli (3/26/21): sometimes a 429 throttling error can occur if test suites run too frequently, so adding a delay

import os
import uuid

import pytest
from python_on_whales import docker
import requests
from stdlib_utils import get_current_file_abs_directory

from ..lambdas.hello_world.src.app import handler

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()


@pytest.fixture(scope="session", name="hello_world_image")
def fixture_hello_world_image():
    tag = f"test-{uuid.uuid4()}:test-{uuid.uuid4()}"
    path_to_dockerfile = os.path.join(
        PATH_TO_CURRENT_FILE, os.pardir, "lambdas", "hello_world"
    )
    image = docker.build(path_to_dockerfile, tags=tag)
    yield image
    docker.image.remove(tag)


def When_the_handler_function_is_invoked__Then_it_returns_a_response():
    assert "Hello" in handler(None, None)


class Given_the_lambda_container_in_running:
    @pytest.fixture(autouse=True)
    def _setup(self, hello_world_image):
        running_container = docker.run(
            hello_world_image, detach=True, remove=True, publish=[(9000, 8080)]
        )
        yield
        docker.container.kill(running_container)

    def When_the_lambda_in_invoked__Then_it_returns_a_response(self):
        r = requests.post(
            "http://localhost:9000/2015-03-31/functions/function/invocations", data="{}"
        )
        assert r.status_code == 200
        assert "Hello from" in r.text

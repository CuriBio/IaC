import os
import sys
from unittest.mock import Mock

from stdlib_utils import resource_path


def import_lambda(lambda_name, mock_imports=None):
    """Return module loaded directly from source file."""

    # mock imports only needed in lambdas to avoid install solely for testing
    if mock_imports:
        for mod_to_mock in mock_imports:
            sys.modules[mod_to_mock] = Mock()

    sys.path.append(resource_path(os.path.join(os.pardir, "src", "lambdas", lambda_name, "src")))
    error = None

    try:
        import app
    except Exception as e:
        error = e

    sys.path.pop()

    if error:
        raise error

    sys.modules[lambda_name] = sys.modules["app"]
    del sys.modules["app"]

    return app

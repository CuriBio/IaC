import importlib.machinery
import os
import sys
import types
from unittest.mock import Mock

from stdlib_utils import resource_path


def import_lambda(lambda_name, mock_imports=None):
    """Return module loaded directly from source file."""

    # mock imports only needed in lambdas to avoid install solely for testing
    if mock_imports:
        for mod_to_mock in mock_imports:
            sys.modules[mod_to_mock] = Mock()

    mod_path = resource_path(os.path.join(os.pardir, "src", "lambdas", lambda_name, "src", "app.py"))
    loader = importlib.machinery.SourceFileLoader(lambda_name, mod_path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod

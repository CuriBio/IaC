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
    
    path_to_lambda_src = resource_path(os.path.join(os.pardir, "src", "lambdas", lambda_name, "src"))

    path_to_lib = os.path.join(path_to_lambda_src, "lib")
    if os.path.isdir(path_to_lib):
        lib_files = os.listdir(path_to_lib)
        for file_name in lib_files:
            if file_name.endswith(".py") and "__init__" not in file_name:
                mod_name = file_name.split(".")[0]
                path_to_lib_file = os.path.join(path_to_lib, file_name)
                loader = importlib.machinery.SourceFileLoader(mod_name, path_to_lib_file)
                lib_mod = types.ModuleType(loader.name)
                loader.exec_module(lib_mod)
                sys.modules[f"lib.{mod_name}"] = lib_mod

    mod_path = os.path.join(path_to_lambda_src, "app.py")
    loader = importlib.machinery.SourceFileLoader(lambda_name, mod_path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod


import importlib.machinery
import os
import types


def import_lambda(lambda_name):
    """Return module loaded directly from source file."""
    mod_path = os.path.join(os.pardir, os.pardir, "src", "lambdas", lambda_name, "src", "app.py")
    loader = importlib.machinery.SourceFileLoader(lambda_name, mod_path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)
    return mod

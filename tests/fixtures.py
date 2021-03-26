# -*- coding: utf-8 -*-
"""Global fixtures across the test suite."""
import os

from stdlib_utils import get_current_file_abs_directory

PATH_TO_CURRENT_FILE = get_current_file_abs_directory()
PATH_TO_INFRA_DIR = os.path.join(PATH_TO_CURRENT_FILE, os.pardir, "infra")

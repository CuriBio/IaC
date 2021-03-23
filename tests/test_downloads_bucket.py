# -*- coding: utf-8 -*-


def test_formats(tf_workspace_name):
    assert isinstance(tf_workspace_name, str)
    print(f"Workspace name in pytest: {tf_workspace_name}")  # allow-print

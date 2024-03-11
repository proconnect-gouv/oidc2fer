#!/usr/bin/env python
"""
OIDC2FER's sandbox management script.
"""
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oidc2fer.settings")
    os.environ.setdefault("DJANGO_CONFIGURATION", "Development")

    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)

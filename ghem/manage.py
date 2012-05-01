#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ghem.settings")
    os.environ.setdefault("DRMAA_LIBRARY_PATH", "/opt/sge/lib/lx24-amd64/libdrmaa.so.1.0")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)

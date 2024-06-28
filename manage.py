#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from django.conf import settings


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    if 'test' not in sys.argv and 'migrate' not in sys.argv:
        if settings.SCHEDULER == 0:
            from solar.create import create_task
            from solar.utils import create_background_task
            create_task()
            create_background_task()
            settings.SCHEDULER = 1
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

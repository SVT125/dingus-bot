#!/usr/bin/env python
from secrets import *
import os
import sys
import bot

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dingus_bot.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError:
        # The above import may fail for some other reason. Ensure that the
        # issue is really that Django is missing to avoid masking other
        # exceptions on Python 2.
        try:
            import django
        except ImportError:
            raise ImportError(
                "Couldn't import Django. Are you sure it's installed and "
                "available on your PYTHONPATH environment variable? Did you "
                "forget to activate a virtual environment?"
            )
        raise
    # TODO - Run as async task
    bot = bot.get_bot()
    bot.run(DISCORD_TOKEN)
    # execute_from_command_line(sys.argv)

import os
import sys

from django.apps import AppConfig


class HealthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Health'

    def ready(self):
        if _should_start_scheduler():
            from .scheduler import start_health_check_scheduler

            start_health_check_scheduler()


def _should_start_scheduler():
    if os.getenv('HEALTH_CHECK_SCHEDULER_ENABLED', 'true').strip().lower() not in {
        '1',
        'true',
        'yes',
        'on',
    }:
        return False

    management_commands = {
        'check',
        'collectstatic',
        'makemigrations',
        'migrate',
        'shell',
        'test',
    }
    if any(command in sys.argv for command in management_commands):
        return False

    if 'runserver' in sys.argv:
        return os.getenv('RUN_MAIN') == 'true'

    return any(server in sys.argv[0].lower() for server in ('gunicorn', 'uwsgi', 'daphne'))

import os

from django.core.management.base import BaseCommand, CommandError

from Login.models import qr_scanner_login


class Command(BaseCommand):
    help = 'Create or update the scanner login from environment variables.'

    def handle(self, *args, **options):
        username = os.getenv('QRSCANNER_LOGIN_USERNAME', '').strip()
        password = os.getenv('QRSCANNER_LOGIN_PASSWORD', '')

        if not username or not password:
            raise CommandError(
                'QRSCANNER_LOGIN_USERNAME and QRSCANNER_LOGIN_PASSWORD must be set.'
            )

        user, created = qr_scanner_login.objects.get_or_create(qr_scanned_name=username)
        user.set_password(password)
        user.save(update_fields=['qr_scanned_password'])

        action = 'Created' if created else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} scanner login for {username}'))

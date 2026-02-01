import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create superuser from environment variables'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', '')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                'DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD must be set'
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f'User "{username}" already exists'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created successfully'))

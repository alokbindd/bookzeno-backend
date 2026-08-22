import os

from decouple import config
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create the default admin/superuser if it does not exist"

    def handle(self, *args, **option):
        User = get_user_model()

        username = config("DJANGO_ADMIN_USERNAME")
        email = config("DJANGO_ADMIN_EMAIL")
        password = config("DJANGO_ADMIN_PASSWORD")

        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_ADMIN_USERNAME or DJANGO_ADMIN_PASSWORD not set. "
                    "Skipping admin creation."
                )
            )

            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user '{username}' already exists. Nothing to do."
                )
            )

            return

        user = User.objects.create_superuser(
            username=username,
            email=email or "",
            password=password,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Superuser '{user.username}' created successfully."
            )
        )

        
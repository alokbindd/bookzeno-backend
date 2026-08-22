from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load BookZeno book and category data from books_data.json"

    def handle(self, *args, **options):
        fixture_path = Path("books_data.json")

        if not fixture_path.exists():
            self.stdout.write(
                self.style.ERROR(
                    "books_data.json not found in the project root."
                )
            )
            return

        self.stdout.write("Loading book data...")

        call_command("loaddata", str(fixture_path))

        self.stdout.write(
            self.style.SUCCESS(
                "Book and category data loaded successfully."
            )
        )
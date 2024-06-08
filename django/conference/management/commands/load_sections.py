from django.core.management.base import BaseCommand
from ...models import Section

from ...config.conference_config import OPENED_SECTIONS


class Command(BaseCommand):
    help = 'Loads sections to database form conference_config.py'

    def handle(self, *args, **options):
        for section in OPENED_SECTIONS:
            Section.objects.get_or_create(content=section)

from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = 'Load dump of demo database to PostgreSQL'

    def handle(self, *args, **options):
        os.system('docker-compose exec -T db psql -U ${DB_USER} -d ${DB_NAME} < db_dumps/demo_dump.sql')
        self.stdout.write(self.style.SUCCESS('Demo data loaded'))

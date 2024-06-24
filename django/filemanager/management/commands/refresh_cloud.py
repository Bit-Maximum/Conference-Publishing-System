import time

import yadisk
from django.core.management.base import BaseCommand

from publisher.settings import YADISK_TOKEN, YADISK_THESIS_PATH, YADISK_ARTICLE_PATH, YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH
from filemanager.views import compose_document_if_not_exists, clear_garbage


class Command(BaseCommand):
    help = 'Refresh cloud storage: delete outdated & create updated documents'

    def handle(self, *args, **options):
        print("Update thesis")
        clear_garbage(YADISK_THESIS_PATH, YADISK_ORIGINALS_THESIS_PATH, "thesis", exclude_filter={"related_thesis__isnull": True})
        print("Thesis updated")
        print("--------------")
        print("Update articles")
        clear_garbage(YADISK_ARTICLE_PATH, YADISK_ORIGINALS_ARTICLE_PATH, "article", exclude_filter={"related_text__isnull": True})
        print("Articles updated")


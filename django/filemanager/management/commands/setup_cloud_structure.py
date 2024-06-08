import yadisk
from django.core.management.base import BaseCommand

from conference.models import Section
from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH, YADISK_THESIS_PATH, YADISK_ARTICLE_PATH


class Command(BaseCommand):
    help = 'Clean setup cloud structure'

    def handle(self, *args, **options):
        y = yadisk.YaDisk(token=YADISK_TOKEN)
        y.mkdir(YADISK_BASE_PATH)
        y.mkdir(f"{YADISK_BASE_PATH}/Оригиналы")
        y.mkdir(YADISK_ORIGINALS_THESIS_PATH)
        y.mkdir(YADISK_ORIGINALS_ARTICLE_PATH)
        y.mkdir(YADISK_THESIS_PATH)
        y.mkdir(YADISK_ARTICLE_PATH)
        print("Base structure created")

        opened_sections = Section.objects.filter(open=True).values_list("content", flat=True)
        for item in opened_sections:
            y.mkdir(f"{YADISK_THESIS_PATH}/{item}")
        print("Thesis structure created")

        for item in opened_sections:
            y.mkdir(f"{YADISK_ARTICLE_PATH}/{item}")
        print("Article structure created")
        print("Done")

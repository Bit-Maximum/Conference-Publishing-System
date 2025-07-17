import yadisk
from django.core.management.base import BaseCommand

from conference.models import Section
from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, YADISK_MAILINGS_SEND_PROGRAM_PATH, YADISK_MAILINGS_BASE_PATH, YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH, YADISK_THESIS_PATH, YADISK_ARTICLE_PATH, YADISK_ORIGINALS_DIR, YADISK_THESIS_EDITED_PATH, YADISK_ARTICLE_EDITED_PATH


class Command(BaseCommand):
    help = 'Clean setup cloud structure'

    def handle(self, *args, **options):
        y = yadisk.YaDisk(token=YADISK_TOKEN)
        try_to_create_dir(y, YADISK_BASE_PATH)
        try_to_create_dir(y, f"{YADISK_BASE_PATH}/{YADISK_ORIGINALS_DIR}")
        try_to_create_dir(y, YADISK_ORIGINALS_THESIS_PATH)
        try_to_create_dir(y, YADISK_ORIGINALS_ARTICLE_PATH)
        try_to_create_dir(y, YADISK_THESIS_PATH)
        try_to_create_dir(y, YADISK_ARTICLE_PATH)
        try_to_create_dir(y, YADISK_THESIS_EDITED_PATH)
        try_to_create_dir(y, YADISK_ARTICLE_EDITED_PATH)
        try_to_create_dir(y, YADISK_MAILINGS_BASE_PATH)
        try_to_create_dir(y, YADISK_MAILINGS_SEND_PROGRAM_PATH)
        print("Base structure created")

        opened_sections = Section.objects.filter(open=True).values_list("content", flat=True)
        for item in opened_sections:
            try:
                y.mkdir(f"{YADISK_THESIS_PATH}/{item}")
            except Exception as e:
                print(e)
                print(f"Thesis directory already exist: {item}")
        print("Thesis structure created")

        for item in opened_sections:
            try:
                y.mkdir(f"{YADISK_THESIS_EDITED_PATH}/{item}")
            except Exception as e:
                print(e)
                print(f"Thesis edited directory already exist: {item}")
        print("Thesis edited structure created")

        for item in opened_sections:
            try:
                y.mkdir(f"{YADISK_ARTICLE_PATH}/{item}")
            except Exception as e:
                print(e)
                print("-------")
                print(f"Articles directory already exist: {item}")
        print("Article structure created")

        for item in opened_sections:
            try:
                y.mkdir(f"{YADISK_ARTICLE_EDITED_PATH}/{item}")
            except Exception as e:
                print(e)
                print(f"Articles edited directory already exist: {item}")
        print("Articles edited structure created")
        print("Done")


def try_to_create_dir(y, path):
    try:
        y.mkdir(path)
    except Exception as e:
        print(e)
        print(f"Directory already exist: {path}")
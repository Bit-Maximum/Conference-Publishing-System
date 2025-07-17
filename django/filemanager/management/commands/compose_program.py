import os
import shutil

import yadisk
from django.core.management.base import BaseCommand

from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, TEMP_FILE_DIR
from filemanager.views import compose_document_if_not_exists, get_articles_info_by_sections
from filemanager.sourcecode.program import compose_program


class Command(BaseCommand):
    help = 'Compose program of conference & load it to cloud'

    def handle(self, *args, **options):
        data = get_articles_info_by_sections()
        print("Данные собраны")
        temp_dir = os.path.join(TEMP_FILE_DIR, "program")
        path_to_file = os.path.join(temp_dir, "Научная программа.docx")
        os.makedirs(temp_dir)
        try:
            compose_program(
                doc_out=path_to_file,
                data=data
            )
            print("Документ сформирован")

            y = yadisk.YaDisk(token=YADISK_TOKEN)
            y.upload(path_to_file,
                     f"{YADISK_BASE_PATH}/Научная программа.docx",
                     overwrite=True)
            print("Документ загружен на Яндекс.Диск")
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(e)
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return

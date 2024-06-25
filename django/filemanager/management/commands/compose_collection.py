import os
import shutil
import time
from tempfile import NamedTemporaryFile

import yadisk
from django.core.management.base import BaseCommand

from conference.models import ArticleInfo, ArticleText, ArticleThesis, Section

from cms.models import ControlsPage
from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, TEMP_FILE_DIR, YADISK_ARTICLE_PATH, TEMP_IMG_DIR, TEMP_FILE_DIR

from filemanager.views import compose_document_if_not_exists, get_articles_info_by_sections, get_info, get_collection_title_data, compose_article, get_sections_data, clear_editors
from filemanager.sourcecode.collection import compose_collection_imprint, compose_collection_section_heading
from filemanager.sourcecode.compose import compose_document


class Command(BaseCommand):
    help = 'Compose program of conference & load it to cloud'

    def handle(self, *args, **options):
        temp_dir = os.path.join(TEMP_FILE_DIR, "collection")
        path_to_file = os.path.join(temp_dir, f"program.docx")
        # try:
        os.makedirs(temp_dir)

        print("Compose imprint")
        data_title = get_collection_title_data()
        output = compose_collection_imprint(path_to_file, data_title)

        print("Compose sections:")
        section_num = 1
        data_sections = get_sections_data()
        y = yadisk.YaDisk(token=YADISK_TOKEN)
        for section, articles_ids in data_sections.items():
            if len(articles_ids) < 0:
                break
            print(f"Section {section} ({section_num}): {len(articles_ids)} articles")
            compose_collection_section_heading(output, path_to_file, section_num, section)
            for i, artile_id in enumerate(articles_ids):
                print("-----")
                data_article, lst_updated, missing = get_info(artile_id, "article")
                compose_article(output, path_to_file, data_article, y)
                time.sleep(2)

                if i < len(articles_ids) - 1:
                    output.add_page_break()
            if section_num < len(data_sections):
                output.add_page_break()
            section_num += 1
        output.save(path_to_file)
        print("Collection ready")

        y.upload(path_to_file,
                 f"{YADISK_BASE_PATH}/Сборник трудов конференции.docx",
                 overwrite=True)
        print("Document uploaded to cloud")
        shutil.rmtree(temp_dir)
        # except Exception as e:
        #     print(e)
        #     try:
        #         shutil.rmtree(temp_dir)
        #     except Exception:
        #         pass

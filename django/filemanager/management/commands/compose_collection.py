import os
import shutil
import time
from tempfile import NamedTemporaryFile

import yadisk
from django.core.management.base import BaseCommand

from conference.models import ArticleInfo, ArticleText, ArticleThesis, Section
# from conference.config.conference_config import COLLECTION_IMPRINT
from cms.models import ControlsPage
from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, TEMP_FILE_DIR, YADISK_ARTICLE_PATH, TEMP_IMG_DIR, TEMP_FILE_DIR

from filemanager.views import compose_document_if_not_exists, get_articles_info_by_sections, get_info
from filemanager.sourcecode.collection import compose_collection_imprint, compose_collection_section_heading
from filemanager.sourcecode.compose import compose_document


class Command(BaseCommand):
    help = 'Compose program of conference & load it to cloud'

    def handle(self, *args, **options):
        try:
            temp_dir = os.path.join(TEMP_FILE_DIR, "collection")
            path_to_file = os.path.join(temp_dir, f"program.docx")
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
        except Exception as e:
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass


def get_collection_title_data():
    raw_data = ControlsPage.objects.first().imprint[0].value
    data = {
        "УДК": raw_data.get('udk'),
        "ББК": raw_data.get('bbk'),
        "Дата публикации": raw_data.get('publication_date'),
        "Библиография": {"Заглавие": raw_data.get('title'),
                         "Описание": raw_data.get('description'),
                         "Город": raw_data.get('city'), "Дата": raw_data.get('conference_date'), "ISBN": raw_data.get('isbn'),
                         "URL": raw_data.get('url'),
                         "Издательство": {"Город": raw_data.get('publishing_city'),
                                          "Название": raw_data.get('publishing_place'),
                                          "Год": raw_data.get('publication_date').year}},
        "Выпускные данные": {"Название": raw_data.get('release').get('organisation'),
                             "Индекс": raw_data.get('release').get('post_code'),
                             "Адрес": raw_data.get('release').get('address'),
                             "E-mail": raw_data.get('release').get('email'),
                             "Телефон": raw_data.get('release').get('phone'),
                             "Copyright": raw_data.get('release').get('copyrite_text'),
                             "Год": raw_data.get('publication_date').year},
        "Аннотация": raw_data.get('annotation').split('\n'),
        "Ред. коллегия": clear_editors(ControlsPage.objects.first().editors[0].value)
    }
    return data


def clear_editors(editors_raw_list):
    result = []
    for editor in editors_raw_list:
        result.append({"ФИО": editor.get('name'), "Должность": editor.get('position')})
    return result


def get_sections_data():
    sections = Section.objects.filter(
        open=True
    ).values_list('id', 'content')

    result = {}
    for section in sections:
        result[section[1]] = ArticleInfo.objects.filter(section=section[0], is_winner=True, related_text__isnull=False).values_list('id', flat=True).distinct()
    return result


def compose_article(doc, path_to_file, data, cloud=None):
    with NamedTemporaryFile(suffix='.docx') as original_file:
        if cloud is None:
            cloud = yadisk.YaDisk(token=YADISK_TOKEN)
        print(data.get('query'))
        cloud.download(f"{YADISK_ARTICLE_PATH}/{data.get('section').get('content')}/{data.get('query')}.docx", original_file)

        original_file.seek(0)
        print("Compose doc")
        compose_document(
            doc_in=original_file,
            doc_out=doc,
            data=data,
            session_num=data.get('section').get('id'),
            img_dir=os.path.join(TEMP_IMG_DIR, "collection"),
            doc_type="collection",
            path_to_file_out=path_to_file
        )

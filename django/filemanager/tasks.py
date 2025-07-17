from celery import shared_task

import os
import time
import shutil
import yadisk

from conference.models import Section
from filemanager.sourcecode.program import compose_program
from filemanager.sourcecode.collection import compose_collection_imprint, compose_collection_section_heading
from filemanager.views import (clear_garbage, compose_document_if_not_exists, get_articles_info_by_sections, get_info,
                               get_collection_title_data, clear_editors, get_sections_data, compose_article)
from publisher.settings import (YADISK_TOKEN, YADISK_BASE_PATH, YADISK_ORIGINALS_THESIS_PATH,
                                YADISK_ORIGINALS_ARTICLE_PATH, YADISK_THESIS_PATH, YADISK_ARTICLE_PATH,
                                TEMP_FILE_DIR, YADISK_ORIGINALS_DIR, YADISK_MAILINGS_SEND_PROGRAM_PATH,
                                YADISK_MAILINGS_BASE_PATH)


def try_to_create_dir(y, path):
    try:
        y.mkdir(path)
    except Exception as e:
        print(e)
        print(f"Directory already exist: {path}")


@shared_task
def task_setup_cloud_structure():
    y = yadisk.YaDisk(token=YADISK_TOKEN)
    try_to_create_dir(y, YADISK_BASE_PATH)
    try_to_create_dir(y, f"{YADISK_BASE_PATH}/{YADISK_ORIGINALS_DIR}")
    try_to_create_dir(y, YADISK_ORIGINALS_THESIS_PATH)
    try_to_create_dir(y, YADISK_ORIGINALS_ARTICLE_PATH)
    try_to_create_dir(y, YADISK_THESIS_PATH)
    try_to_create_dir(y, YADISK_ARTICLE_PATH)
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
            y.mkdir(f"{YADISK_ARTICLE_PATH}/{item}")
        except Exception as e:
            print(e)
            print("-------")
            print(f"Articles directory already exist: {item}")
    print("Article structure created")
    print("Done")


@shared_task
def task_refresh_cloud():
    print("Update thesis")
    clear_garbage(YADISK_THESIS_PATH, YADISK_ORIGINALS_THESIS_PATH, "thesis",
                  exclude_filter={"related_thesis__isnull": True})
    print("Thesis updated")
    print("--------------")
    print("Update articles")
    clear_garbage(YADISK_ARTICLE_PATH, YADISK_ORIGINALS_ARTICLE_PATH, "article",
                  exclude_filter={"related_text__isnull": True})
    print("Articles updated")
    return


@shared_task
def task_compose_program():
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


@shared_task
def task_compose_collection():
    temp_dir = os.path.join(TEMP_FILE_DIR, "collection")
    path_to_file = os.path.join(temp_dir, f"program.docx")
    try:
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

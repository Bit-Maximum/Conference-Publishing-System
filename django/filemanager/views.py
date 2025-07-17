import io
import os
import shutil
import time
from tempfile import NamedTemporaryFile

import yadisk
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, JsonResponse

from conference.models import ArticleInfo, CustomUser, Section, AuthorInfo, Source
from cms.models import ControlsPage, SectionModerator
from publisher.settings import YADISK_TOKEN, YADISK_BASE_PATH, YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH, YADISK_THESIS_PATH, TEMP_IMG_DIR, TEMP_FILE_DIR, YADISK_ARTICLE_PATH, YADISK_THESIS_EDITED_PATH, YADISK_ARTICLE_EDITED_PATH
from filemanager.sourcecode.collection import compose_collection_imprint, compose_collection_section_heading
from filemanager.sourcecode.program import compose_program
from filemanager.sourcecode.compose import compose_document

from wagtail.models import Site


def upload_file(file_or_path, path_to, cloud=None):
    try:
        if cloud is None:
            cloud = yadisk.YaDisk(token=YADISK_TOKEN)
        cloud.upload(file_or_path, path_to, overwrite=True)
    except Exception as e:
        print("YaDisk error", e)


def get_meta_cloud(path, cloud=None):
    try:
        if cloud is None:
            cloud = yadisk.YaDisk(token=YADISK_TOKEN)
        meta = cloud.get_meta(path)
    except Exception as e:
        meta = None
    return meta


def check_file_exists_cloud(path, cloud=None):
    try:
        if cloud is None:
            cloud = yadisk.YaDisk(token=YADISK_TOKEN)
        exists = cloud.exists(path)
    except Exception as e:
        exists = False
    return exists


def get_info(article_id, doc_type=None, article=None):
    if not article:
        article = ArticleInfo.objects.filter(pk=article_id).first()
    section = article.section
    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors = AuthorInfo.objects.filter(user_id__in=[u.id for u in users])
    sources = Source.objects.filter(article=article.id).order_by('content') if doc_type != "collection" else []

    last_update = [article.last_updated] + [author.last_updated for author in authors] + [u.last_updated for u in users] + [s.last_updated for s in sources]
    authors_names = [u.fullname for u in users] if doc_type != "collection" else [u.fullname_reverse for u in users]
    data = {
        "query": article.title.replace(":", ".").rstrip('.'),
        "title": article.title.strip('"').rstrip('.'),
        "abstract": article.abstract,
        "keywords": article.keywords,
        "authors": {
            "names": authors_names,
            "cities": [a.address for a in authors]
        },
        "adviser": {
            "degree": article.adviser_degree,
            "academic_title": article.academic_title,
            "job_title": article.job_title,
            "job": article.adviser_job,
            "name": article.fullname
        },
        "sources": [s.content for s in sources],
        "grant": article.grant,
        "section": {
            "id": section.pk,
            "content": section.content.strip()
        }
    }
    allow_no_source = ControlsPage.objects.first().allow_no_source
    missing = []
    if doc_type == "article" or doc_type == "collection":
        if not data.get("abstract"):
            missing.append("Отсутствует аннотация.")
        if not data.get("keywords", None) or data.get("keywords") == "":
            missing.append("Отсутствуют ключевые слова.")

    if len(data.get("authors").get("names")) <= 0:
        missing.append("Нет авторов.")
    if len(data.get("authors").get("cities")) != len(data.get("authors").get("names")):
        missing.append("Не у всех авторов указан город и/или место учёбы.")
    if doc_type != "collection" and not allow_no_source and len(data.get("sources")) <= 0:
        missing.append("Не указано ни одной библиографической ссылки на источник.")

    if data.get("adviser").get("name") == 'Не указан':
        data["adviser"] = None

    return data, last_update, missing


def up_to_date(date, lst_updated):
    for item in lst_updated:
        if item > date:
            return False
    return True


def get_thesis_or_article(request, doc_type, article_id, need_check=None):
    if doc_type == "thesis":
        cloud_originals_path = YADISK_ORIGINALS_THESIS_PATH
        cloud_doc_path = YADISK_THESIS_PATH
    elif doc_type == "article":
        cloud_originals_path = YADISK_ORIGINALS_ARTICLE_PATH
        cloud_doc_path = YADISK_ARTICLE_PATH
    else:
        return JsonResponse({"errors": ["Запрашиваемого типа документов не существует."]}, status=400)

    need_edit = ControlsPage.objects.first().is_editing_on
    y = yadisk.YaDisk(token=YADISK_TOKEN)
    orig_file = get_meta_cloud(f"{cloud_originals_path}/{article_id}.docx", cloud=y)
    if not orig_file:
        if need_check:
            return JsonResponse({"errors": ["При загрузке документа произошла ошибка. Пожалуйста, повторите попытку позже."]}, status=404)
        return JsonResponse({"errors": ["В данный момент сервис не может обработать ваш запрос. Пожалуйста, повторите попытку позже."]}, status=404)

    try:
        data, lst_updated, missing = get_info(article_id, doc_type=doc_type)
        if need_edit and len(missing) > 0:
            return JsonResponse({"errors": missing}, status=424)
    except Exception as e:
        return JsonResponse({"errors": ["Не все обязательные поля заполнены. Для исправления ошибки обратитесь к инструкции."]}, status=424)

    if not need_check and check_file_exists_cloud(f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", cloud=y):
        cloud_meta = get_meta_cloud(f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", cloud=y)
        if not need_edit or up_to_date(cloud_meta.modified, lst_updated + [orig_file.modified]):
            with NamedTemporaryFile(suffix='.docx') as temp_file:
                try:
                    y.download(f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", temp_file)
                except Exception as e:
                    return JsonResponse(
                        {"errors": ["Во время скачивания документа произошла ошибка. Попробуйте ещё раз позже."]},
                        status=503)
                try:
                    temp_file.seek(0)
                    file_bytes = temp_file.read()
                except Exception as e:
                    return JsonResponse(
                        {"errors": ["Во чтения документа произошла ошибка. Попробуйте ещё раз позже."]},
                        status=523)
                try:
                    response = FileResponse(io.BytesIO(file_bytes), as_attachment=True, filename=f"{data.get('title')}.docx")
                    return response
                except Exception as e:
                    return JsonResponse({"errors": ["Во время отправки документа произошла ошибка. Попробуйте ещё раз позже."]},
                                        status=502)

    with NamedTemporaryFile(suffix='.docx') as original_file:
        try:
            y.download(f"{cloud_originals_path}/{article_id}.docx", original_file)
            original_file.seek(0)
            if not need_edit:
                y.upload(original_file, f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", overwrite=True)
                original_file.seek(0)
                file_bytes = original_file.read()
            else:
                temp_dir = os.path.join(TEMP_FILE_DIR, doc_type, str(request.user.id))
                path_to_file = os.path.join(temp_dir, f"{article_id}.docx")
                os.makedirs(temp_dir)
                compose_document(
                    doc_in=original_file,
                    doc_out=path_to_file,
                    data=data,
                    session_num=request.user.id,
                    img_dir=os.path.join(TEMP_IMG_DIR, doc_type),
                    doc_type=doc_type
                )
                y.upload(path_to_file, f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", overwrite=True)
                with open(path_to_file, "rb") as temp_file:
                    file_bytes = temp_file.read()
                shutil.rmtree(temp_dir)

            if need_check:
                return JsonResponse({"massage": ["Документ успешно загружен."]}, status=202)
            response = FileResponse(io.BytesIO(file_bytes), as_attachment=True, filename=f"{data.get('title')}.docx")
            return response

        except Exception as e:
            print(e)
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            if need_check:
                return JsonResponse(
                    {"errors": ["При отправке документа произошла ошибка. Пожалуйста, повторите попытку позже."]}, status=400)
            return JsonResponse({"errors": ["В данный момент сервис не доступен. Попробуйте ещё раз позже."]}, status=400)


def compose_document_if_not_exists(article_id, doc_type, cloud=None):
    if doc_type == "thesis":
        cloud_originals_path = YADISK_ORIGINALS_THESIS_PATH
        cloud_doc_path = YADISK_THESIS_PATH
        cloud_edited_doc_path = YADISK_THESIS_EDITED_PATH
    elif doc_type == "article":
        cloud_originals_path = YADISK_ORIGINALS_ARTICLE_PATH
        cloud_doc_path = YADISK_ARTICLE_PATH
        cloud_edited_doc_path = YADISK_ARTICLE_EDITED_PATH
    else:
        raise Http404("Неизвестный тип документа")

    if cloud is None:
        cloud = yadisk.YaDisk(token=YADISK_TOKEN)

    try:
        need_edit = ControlsPage.objects.first().is_editing_on
        orig_file = get_meta_cloud(f"{cloud_originals_path}/{article_id}.docx", cloud=cloud)
        if not orig_file:
            return 404

        data, lst_updated, missing = get_info(article_id)
        if need_edit and len(missing) > 0:
            return 424
    except Exception as e:
        return 520

    if check_file_exists_cloud(f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", cloud=cloud):
        cloud_meta = get_meta_cloud(f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", cloud=cloud)
        if not need_edit and up_to_date(cloud_meta.modified, lst_updated + [orig_file.modified]):
            return 208

    with NamedTemporaryFile(suffix='.docx') as original_file:
        try:
            cloud.download(f"{cloud_originals_path}/{article_id}.docx", original_file)
            original_file.seek(0)

            cloud.upload(original_file, f"{cloud_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", overwrite=True)
            if not need_edit:
                return 200

            temp_dir = os.path.join(TEMP_FILE_DIR, doc_type, f"{article_id}_{article_id}")
            path_to_file = os.path.join(temp_dir, f"{article_id}.docx")
            os.makedirs(temp_dir)
            compose_document(
                doc_in=original_file,
                doc_out=path_to_file,
                data=data,
                session_num=f"{article_id}_{article_id}",
                img_dir=os.path.join(TEMP_IMG_DIR, doc_type),
                doc_type=doc_type
            )

            cloud.upload(path_to_file, f"{cloud_edited_doc_path}/{data.get('section').get('content')}/{data.get('query')}.docx", overwrite=True)
            shutil.rmtree(temp_dir)
            return 200

        except Exception as e:
            try:
                print(e)
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return 520


@login_required
def download_program(request):
    if not request.user.is_staff:
        raise PermissionDenied()

    data = get_articles_info_by_sections()

    temp_dir = os.path.join(TEMP_FILE_DIR, "program")
    path_to_file = os.path.join(temp_dir, "Научная программа.docx")
    try:
        os.makedirs(temp_dir)
        compose_program(
            doc_out=path_to_file,
            data=data
        )

        y = yadisk.YaDisk(token=YADISK_TOKEN)
        y.upload(path_to_file,
                 f"{YADISK_BASE_PATH}/Научная программа.docx",
                 overwrite=True)

        with open(path_to_file, "rb") as temp_file:
            file_bytes = temp_file.read()
        shutil.rmtree(temp_dir)
        response = FileResponse(io.BytesIO(file_bytes), as_attachment=True,
                                filename=f"Научная программа.docx")
        return response
    except Exception as e:
        print(e)
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass
        return JsonResponse({"errors": ["Во время отправки документа произошла ошибка. Попробуйте ещё раз позже."]}, status=500)


def get_articles_info_by_sections():
    data = []
    moderators = {}
    conference_name = str(Site.objects.first().site_name)
    sections = Section.objects.all().order_by('content')
    moderators_raw = SectionModerator.objects.all()
    for moderator in moderators_raw:
        item = {"degree": moderator.degree,
                "academic_title":  moderator.academic_title,
                "job_title": moderator.job_title,
                "job": moderator.job,
                "name": moderator.name}
        moderators[moderator.section.strip()] = item

    for section in sections:
        section_data = dict()
        section_data['section'] = section.content.strip()
        section_data['moderator'] = moderators.get(section.content.strip(), None)

        articles = []
        for article in ArticleInfo.objects.filter(section=section, rejected=None):
            article_data = dict()
            article_data['title'] = article.title
            article_data['authors'] = ", ".join([item.initials for item in article.authors.all()])

            adviser = article.adviser_info
            article_data['adviser'] = {
                'name': adviser[0],
                "info": adviser[1]
            }
            articles.append(article_data)
        section_data['articles'] = articles
        section_data['conference_name'] = conference_name
        data.append(section_data)
    return data


def clear_garbage(base_path, originals_path, doc_type, exclude_filter=None):
    y = yadisk.YaDisk(token=YADISK_TOKEN)

    cloud = dict()
    queries = []
    path = []
    print(f"Document assist status: {ControlsPage.objects.first().is_editing_on}")
    print("Collecting Cloud Info", end="")

    opened_sections = Section.objects.filter(open=True).values_list("content", flat=True)
    for section in opened_sections:
        print('.', end='')
        section = section.strip()
        data = list(y.listdir(f"{base_path}/{section}"))
        cloud[section] = data
        for item in data:
            queries.append(item.name.rstrip(".docx"))
            path.append(item.path)
    print()

    articles = ArticleInfo.objects.exclude(**exclude_filter)
    meta = [(item, item.title.replace(":", ".")) for item in articles]
    titles = [item[1] for item in meta]

    queries_to_delete = []
    for i in range(len(queries)):
        if queries[i] not in titles:
            queries_to_delete.append(path[i])

    print(f"Docs on server: {articles[0:3]}...")
    print(f"Docs on cloud: {queries[0:3]}...")
    print(f"Will be DELETED: {queries_to_delete[0:3]}...")
    print(f"On server: {len(articles)}. On cloud: {len(queries)}. To delete: {len(queries_to_delete)}.")

    # print("Deleting extra Docs from cloud")
    # for item in queries_to_delete:
    #     y.remove(item)
    #     time.sleep(1)

    originals_storage = [item.pk for item in articles]
    originals_cloud = [item.name for item in list(y.listdir(originals_path))]

    queries_to_delete = []
    for item in originals_cloud:
        if int(item.rstrip(".docx")) not in originals_storage:
            queries_to_delete.append(item)

    print("---")
    print(f"Originals on server: {originals_storage[0:3]}...")
    print(f"Originals on cloud: {originals_cloud[0:3]}...")
    print(f"Will be DELETED: {queries_to_delete[0:3]}...")
    print(f"Originals on server: {len(originals_storage)}. On cloud: {len(originals_cloud)}. To delete: {len(queries_to_delete)}.")
    print("---")

    # print("Deleting extra originals from cloud")
    # for item in queries_to_delete:
    #     y.remove(f"{originals_path}/{item}")
    #     time.sleep(1)

    print("Recreate outdated Docs")
    size = len(articles)
    fails = []
    missing_original = []
    missing_data = []
    no_need_update = []
    success = []
    for i, item in enumerate(articles):
        if i % 5 == 0:
            print(f"Update: {i} / {size}")

        time.sleep(1)
        res = compose_document_if_not_exists(item.id, doc_type, cloud=y)
        print(res)

        if res == 200:
            success.append(item.title)
        elif res == 404:
            missing_original.append(item.title)
        elif res == 208:
            no_need_update.append(item.title)
        elif res == 424:
            missing_data.append(item.title)
        else:
            fails.append(item.title)

    print("---")
    print(f"Updated: {len(success)}")
    print(f"No need update: {len(no_need_update)}")
    print(f"Missing original: {len(missing_original)}")
    print(f"Missing data: {len(missing_data)}")
    print(f"Compose failed count: {len(fails)}")
    print("---")
    for item in missing_original:
        print(f"Missing original: {item}")
    print("---")
    for item in fails:
        print(f"Failed: {item}")
    print("---")


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
        position = editor.get('position') if editor.get('position') != '-' else None
        result.append({"ФИО": editor.get('name'), "Должность": position})
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


def compose_collection(request):
    if not request.user.is_staff:
        raise PermissionDenied()

    temp_dir = os.path.join(TEMP_FILE_DIR, "collection")
    path_to_file = os.path.join(temp_dir, f"program.docx")
    os.makedirs(temp_dir)
    try:
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


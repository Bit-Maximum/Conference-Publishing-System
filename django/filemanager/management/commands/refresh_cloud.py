import time

import yadisk
from django.core.management.base import BaseCommand

from conference.models import ArticleInfo, ArticleText, ArticleThesis, Section
from publisher.settings import YADISK_TOKEN, YADISK_THESIS_PATH, YADISK_ARTICLE_PATH, YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH
from filemanager.views import compose_document_if_not_exists


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


def clear_garbage(base_path, originals_path, doc_type, exclude_filter=None):
    y = yadisk.YaDisk(token=YADISK_TOKEN)

    cloud = dict()
    queries = []
    path = []
    print("Collect Cloud Info", end="")

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
    if doc_type == "thesis":
        confirm = input(f"On server: {len(articles)}. On cloud: {len(queries)}. To delete: {len(queries_to_delete)}. Continue? (y/N): ")
        if confirm.lower() != 'y':
            print("Operation canceled")
            return
    else:
        print(f"On server: {len(articles)}. On cloud: {len(queries)}. To delete: {len(queries_to_delete)}.")

    print("Deleting extra Docs from cloud")
    for item in queries_to_delete:
        y.remove(item)
        time.sleep(1)

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
    print("Deleting extra originals from cloud")
    for item in queries_to_delete:
        y.remove(f"{originals_path}/{item}")
        time.sleep(1)

    print("Recreate outdated Docs")
    size = len(articles)
    fails = []
    missing_original= []
    no_need_update = []
    success = []
    for i, item in enumerate(articles):
        if i % 5 == 0:
            print(f"Update: {i} / {size}")

        time.sleep(1)
        res = compose_document_if_not_exists(item.id, doc_type, cloud=y)
        if res is None:
            no_need_update.append(item.title)
        elif isinstance(res, bool) and res:
            if not res:
                fails.append(item.title)
            else:
                success.append(item.title)
        elif isinstance(res, int):
            if res == 404:
                missing_original.append(item.title)
            else:
                fails.append(item.title)
        else:
            success.append(item.title)

    print("---")
    print(f"Updated: {len(success)}")
    print(f"No need update: {len(no_need_update)}")
    print(f"Missing original: {len(missing_original)}")
    print(f"Compose failed count: {len(fails)}")
    print("---")
    for item in missing_original:
        print(f"Missing original: {item}")
    print("---")
    for item in fails:
        print(f"Failed: {item}")
    print("---")

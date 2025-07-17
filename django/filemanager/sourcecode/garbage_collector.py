from ...conference.models import ArticleThesis, ArticleText, ArticleInfo


def clear_outdated_files():
    natural = ArticleInfo.objects.all().select_related('related_thesis')
    cloud = get_cloud_structure("thesis")

    outdated = filter_outdated(natural, cloud)
    upload_new_documents(outdated)
    clear_thesis(outdated)

    natural = ArticleInfo.objects.all().select_related('related_thesis')
    cloud = get_cloud_structure("article")

    outdated = filter_outdated(natural, cloud)
    upload_new_documents(outdated)
    clear_article(outdated)


def clear_thesis(outdated):
    for item in outdated:
        remove_file_from_cloud(item)


def clear_article(outdated):
    for item in outdated:
        remove_file_from_cloud(item)


def get_cloud_structure(doc_type: str):
    if doc_type == "thesis":
        pass
    if doc_type == "article":
        pass
    if doc_type == "collection":
        pass
    return {}


def filter_outdated(natural, cloud):
    return []


def remove_file_from_cloud(file):
    pass


def upload_new_documents(outdated):
    for item in outdated:
        compose_document()
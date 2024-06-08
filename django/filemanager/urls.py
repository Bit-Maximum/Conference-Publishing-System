from django.urls import path

from . import views


urlpatterns = [
    path("download/<str:doc_type>/<int:article_id>", views.get_thesis_or_article, name="get_thesis_or_article"),
    path("download/<str:doc_type>/<int:article_id>/<int:need_check>", views.get_thesis_or_article, name="check_thesis_or_article"),
    path("download/program", views.download_program, name="download_program"),
    path("download/collection", views.compose_collection, name="download_collection")
]

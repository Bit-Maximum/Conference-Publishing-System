import json
import os
import re

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect, Http404, FileResponse
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils import timezone

from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django_email_verification import send_email

from .models import CustomUser, AuthorInfo, Section, SectionEditor, ArticleInfo, ArticleText, Comment, Source, \
    ArticleThesis, Consent, TechnicalWork, CommentAttachment
from cms.models import HomePage, ControlsPage, BaseMailPage
from cms.views import get_mail_context
from .forms import FilterArticleForm, ArticleTextForm, ArticleThesisForm, ConsentForm, EmailChangeForm, CommentAttachmentForm

from mailings.views import send_mail_attachments
from filemanager.views import upload_file, up_to_date
from publisher.settings import YADISK_ORIGINALS_THESIS_PATH, YADISK_ORIGINALS_ARTICLE_PATH, EMAIL_HOST_USER, MEDIA_ROOT, CLOUD_BASE_URL, MEDIA_ROOT, DEFAULT_FROM_EMAIL
from .config.conference_config import EDUCATION_LEVELS


def select_outdated(date, updated):
    res = []
    for key, value in updated.items():
        if not up_to_date(date, value):
            res.append(key)
    return res


# def index(request):
#     """Главная страница. Отображает информацию о конференции."""
#     sections = Section.objects.filter(open=True).values_list("content", flat=True)
#     return render(request, "conference/index.html", {
#         "sections": sections, "registration": REGISTRATION_OPEN, "program_ready": PROGRAM_READY
#     })


@login_required
@ensure_csrf_cookie
def profile(request):
    """Профиль пользователя."""
    user = CustomUser.objects.filter(id=request.user.id).first()
    if user.is_staff:
        if not SectionEditor.objects.filter(user_id=user.id).exists():
            return HttpResponseRedirect(reverse("staff"))
        editor = SectionEditor.objects.filter(user=user.id).first()
        section = Section.objects.filter(id=editor.section.id).first()
        sections = Section.objects.filter(open=True)
        comments = Comment.objects.filter(editor=editor.id)

        return render(request, "conference/profile/profile_staff.html", {
            "user": user.serialize(),
            "section": section.serialize(),
            "sections": [s.serialize() for s in sections],
            "comments": [c.map_attachments() for c in comments]
        })
    else:
        if AuthorInfo.objects.filter(user_id=user.id).exists():
            author = AuthorInfo.objects.filter(user_id=user.id).first()
            author = author.serialize()
        else:
            author = None
        comments = []
        articles = ArticleInfo.objects.filter(authors=user.id)
        if len(articles) != 0:
            comments = Comment.objects.filter(article__in=articles)
            articles = [a.show_info() for a in articles]
        else:
            articles = None

        confirm_participation = ControlsPage.objects.first().confirm_participation

        context = {
            "user": user.serialize(),
            "author": author,
            "education": EDUCATION_LEVELS.keys(),
            "articles": articles,
            "comments": [c.map_attachments() for c in comments],
            "email_from": DEFAULT_FROM_EMAIL,
            "confirm_participation": confirm_participation
        }

        if not user.is_consent_send:
            context["consent_form"] = ConsentForm()

        return render(request, "conference/profile/profile_author.html", context)


def article(request, article_id, need_check=""):
    """Cтраница просмотра искомой статьи."""
    article = ArticleInfo.objects.filter(id=article_id).first()
    if article is None:
        raise Http404("Доклад не найден")

    sections = Section.objects.filter(open=True)
    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors = AuthorInfo.objects.filter(user_id__in=[u.id for u in users])
    comments = Comment.objects.filter(article_id=article_id)
    sources = Source.objects.filter(article=article.id).order_by('content')

    data = []
    for i in range(len(users)):
        if i >= len(authors):
            data.append(users[i].serialize())
            continue
        data.append(authors[i].serialize() | users[i].serialize())
    authors_ids = [user.id for user in users]

    last_update = {
        "Инормацию о докладе": [article.last_updated],
        "Информацию об авторах": [author.last_updated for author in authors] + [u.last_updated for u in users],
        "Список литературы": [s.last_updated for s in sources]
    }

    thesis = ArticleThesis.objects.filter(article=article_id).first()
    if thesis:
        last_update["Тезисы"] = [thesis.last_updated]
        thesis = thesis.serialize()

    text = ArticleText.objects.filter(article=article_id).first()
    if text:
        last_update["Текст доклада"] = [text.last_updated]
        text = text.serialize()

    if article.editor_approved:
        temp = select_outdated(article.editor_approved, last_update)
        editor_outdated = {
            "items": temp,
            "length": len(temp)
        }
    else:
        editor_outdated = None

    if article.reviewer_approved:
        temp = select_outdated(article.reviewer_approved, last_update)
        reviewer_outdated = {
            "items": temp,
            "length": len(temp)
        }
    else:
        reviewer_outdated = None

    check_thesis = True if need_check == "thesis" and request.method != "POST" else False
    check_text = True if need_check == "text" and request.method != "POST" else False

    keyword_length = ControlsPage.objects.first().keyword_length

    context = {
        "article": article.serialize(),
        "users": [u.serialize() for u in users],
        "authors": data,
        "authors_ids": authors_ids,
        "KEYWORDS_MAX_NUM": keyword_length,
        "sections": [s.serialize() for s in sections],
        "comments": [c.map_attachments() for c in comments],
        "text": text,
        "thesis": thesis,
        "sources": [s.serialize() for s in sources],
        "form_thesis": ArticleThesisForm(),
        "form_text": ArticleTextForm(),
        "editor_outdated": editor_outdated,
        "reviewer_outdated": reviewer_outdated,
        "cloud_base_url": CLOUD_BASE_URL,
        "check_thesis": check_thesis,
        "check_text": check_text,
        "form_comment": CommentAttachmentForm()
        }

    if request.method == "POST":
        form = ArticleTextForm(request.POST, request.FILES)
        if request.user.is_authenticated and form.is_valid():
            if request.user.id in authors_ids:
                if ArticleText.objects.filter(article=article).exists():
                    ArticleText.objects.filter(article=article).first().delete()
                form.save()
                file = ArticleText.objects.filter(article=article).first()
                try:
                    upload_file(file.file.open(), f"{YADISK_ORIGINALS_ARTICLE_PATH}/{article.pk}.docx")
                except Exception as e:
                    pass
                file.file.close()
                return HttpResponseRedirect(reverse("article", args=[article_id, "text"]))
        context["form_text"] = form
    return render(request, "conference/article.html", context)


def delete_article_text(request, article_id):
    """Удаление текста статьи."""

    article = get_object_or_404(ArticleInfo, pk=article_id)
    file = get_object_or_404(ArticleText, article=article.id)

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if request.user.id not in authors_ids:
        raise Http404("Вы не являетесь автором этого доклада")

    file.delete()
    return HttpResponseRedirect(reverse("article", args=[article.id]))


def download_article_text(request, article_id):
    """Форсированое скачивание текста статьи."""
    article = get_object_or_404(ArticleInfo, pk=article_id)
    file = get_object_or_404(ArticleText, article=article.id)

    if not file.file.storage.exists(file.file.name):
        raise Http404("Материал не найден")

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if not request.user.is_staff and (request.user.id not in authors_ids):
        raise Http404("У вас нет доступа для скачивания этого матариала")

    return FileResponse(file.file.open(), as_attachment=True)


def add_article_thesis(request, article_id):
    """Добавление тезисов для статьи."""
    article = ArticleInfo.objects.filter(id=article_id).first()
    if article is None:
        raise Http404("Доклад не найден")

    sections = Section.objects.filter(open=True)
    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors = AuthorInfo.objects.filter(user_id__in=[u.id for u in users])
    comments = Comment.objects.filter(article_id=article_id)
    sources = Source.objects.filter(article=article.id).order_by('content')

    data = []
    for i in range(len(users)):
        if i >= len(authors):
            data.append(users[i].serialize())
            continue
        data.append(authors[i].serialize() | users[i].serialize())
    authors_ids = [user.id for user in users]

    last_update = {
        "Инормацию о докладе": [article.last_updated],
        "Информацию об авторах": [author.last_updated for author in authors] + [u.last_updated for u in users],
        "Список литературы": [s.last_updated for s in sources]
    }

    thesis = ArticleThesis.objects.filter(article=article_id).first()
    if thesis:
        last_update["Тезисы"] = [thesis.last_updated]
        thesis = thesis.serialize()

    text = ArticleText.objects.filter(article=article_id).first()
    if text:
        last_update["Текст доклада"] = [text.last_updated]
        text = text.serialize()

    if article.editor_approved:
        temp = select_outdated(article.editor_approved, last_update)
        editor_outdated = {
            "items": temp,
            "length": len(temp)
        }
    else:
        editor_outdated = None

    if article.reviewer_approved:
        temp = select_outdated(article.reviewer_approved, last_update)
        reviewer_outdated = {
            "items": temp,
            "length": len(temp)
        }
    else:
        reviewer_outdated = None

    keyword_length = ControlsPage.objects.first().keyword_length

    context = {
        "article": article.serialize(),
        "users": [u.serialize() for u in users],
        "authors": data,
        "authors_ids": authors_ids,
        "KEYWORDS_MAX_NUM": keyword_length,
        "sections": [s.serialize() for s in sections],
        "comments": [c.serialize() for c in comments],
        "text": text,
        "thesis": thesis,
        "sources": [s.serialize() for s in sources],
        "form_thesis": ArticleThesisForm(),
        "form_thesis": ArticleThesisForm(),
        "form_text": ArticleTextForm(),
        "editor_outdated": editor_outdated,
        "reviewer_outdated": reviewer_outdated,
        "cloud_base_url": CLOUD_BASE_URL
        }

    if request.method == "POST":
        form = ArticleThesisForm(request.POST, request.FILES)
        if request.user.is_authenticated and form.is_valid():
            if request.user.id in authors_ids:
                if ArticleThesis.objects.filter(article=article).exists():
                    ArticleThesis.objects.filter(article=article).first().delete()
                form.save()
                file = ArticleThesis.objects.filter(article=article).first()
                try:
                    upload_file(file.file.open(), f"{YADISK_ORIGINALS_THESIS_PATH}/{article.pk}.docx")
                except Exception:
                    pass
                file.file.close()
                return HttpResponseRedirect(reverse("article", args=[article_id, "thesis"]))
        context["form_thesis"] = form
    return render(request, "conference/article.html", context)


@login_required
def add_consent(request, user_id):
    """Загрузка согласия на обработку персональных данных."""
    if request.method == "POST":
        owner = get_object_or_404(CustomUser, pk=user_id)

        if request.user.pk != owner.pk:
            raise Http404("Доступ запрещён")

        form = ConsentForm(request.POST, request.FILES)
        if form.is_valid():
            if Consent.objects.filter(user=owner).exists():
                Consent.objects.filter(user=owner).first().delete()
            form.save()
            owner.is_consent_send = True
            owner.save()
    return HttpResponseRedirect(reverse("profile"))


@login_required()
def confirm_participation(request):
    if request.method == "POST":
        user = CustomUser.objects.filter(id=request.user.id).first()
        user.is_participation_confirmed = True
        user.save()
    return HttpResponseRedirect(reverse("profile"))


def delete_article_thesis(request, article_id):
    """Удаление тезисов статьи."""
    article = get_object_or_404(ArticleInfo, pk=article_id)
    file = get_object_or_404(ArticleThesis, article=article.id)

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if request.user.id not in authors_ids:
        raise Http404("Вы не являетесь автором этого доклада")

    file.delete()
    return HttpResponseRedirect(reverse("article", args=[article.id]))


@login_required
def delete_consent(request, user_id):
    """Удаление согласия на обработку персональных данных."""
    owner = get_object_or_404(CustomUser, pk=user_id)
    file = get_object_or_404(Consent, user=owner.id)

    if request.user.pk != owner.pk:
        raise Http404("Вы не являетесь владельцем этого документа")

    file.delete()
    owner.is_consent_send = False
    owner.save()
    return HttpResponseRedirect(reverse("profile"))


def download_article_thesis(request, article_id):
    """Форсированое скачивание тезисов."""
    article = get_object_or_404(ArticleInfo, pk=article_id)
    file = get_object_or_404(ArticleThesis, article=article.id)

    if not file.file.storage.exists(file.file.name):
        raise Http404("Материал не найден")

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if not request.user.is_staff and (request.user.id not in authors_ids):
        raise Http404("У вас нет доступа для скачивания этого матариала")

    return FileResponse(file.file.open(), as_attachment=True)


def download_attachment(self, attachment_id):
    """Форсированое скачивание вложения к комментарию от редакции."""
    file = get_object_or_404(CommentAttachment, pk=attachment_id)

    if not file.file.storage.exists(file.file.name):
        raise Http404("Материал не найден")

    return FileResponse(file.file.open(), as_attachment=True)


@login_required
def download_consent(request, user_id):
    """Форсированое скачивание тезисов."""
    owner = get_object_or_404(CustomUser, pk=user_id)
    file = get_object_or_404(Consent, user=owner.id)

    if not file.file.storage.exists(file.file.name):
        raise Http404("Материал не найден")

    if not request.user.is_staff and request.user.pk != owner.pk:
        raise Http404("У вас нет доступа для скачивания этого матариала")

    return FileResponse(file.file.open(), as_attachment=True)


def add_source(request, article_id):
    """Добавление ссылки на источник к статье."""
    if request.method != "POST":
        return HttpResponseRedirect(reverse("article", args=[article_id]))

    article = get_object_or_404(ArticleInfo, pk=article_id)

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if request.user.id not in authors_ids:
        return Http404("У вас нет доступа для добавление источников к данному докладу")

    content = request.POST.get("source_content").strip()

    if bool(re.match(r"^\d+[.)] ", content)):
        content = ' '.join(content.split()[1:])

    content = content.replace("\n", "")
    content = content.replace("\r", "")

    Source.objects.create(article=article, content=content)
    return HttpResponseRedirect(reverse("article", args=[article_id]))


def delete_source(request, source_id):
    """Удаление ссылки на источник в статье."""
    source = get_object_or_404(Source, pk=source_id)

    users = CustomUser.objects.filter(id__in=source.article.authors.all())
    authors_ids = [user.id for user in users]

    if request.user.id not in authors_ids:
        return Http404("У вас нет доступа для удаления источников данного доклада")

    source.delete()
    return HttpResponseRedirect(reverse("article", args=[source.article.id]))


def library(request):
    """Страница со всеми статьями."""
    if request.method == "POST":
        form = FilterArticleForm(request.POST)

        if form.is_valid():
            authors_info_fields = ["country", "city__icontains", "institution__icontains", "department__icontains",
                                   "major__icontains", "level__icontains", "course", "is_participation_confirmed"]

            article_filters = {}
            author_filters = {}

            for field in form.fields:
                value = form.cleaned_data.get(field, "")
                if value != "" and value is not None:
                    if value == "True" or value == "False":
                        value = True if value == "True" else False

                    if field in authors_info_fields:
                        author_filters[field] = value
                    else:
                        article_filters[field] = value

            if len(author_filters) != 0:
                selected_users = article_filters.get("authors__in", [])
                searched_users = CustomUser.objects.filter(id__in=AuthorInfo.objects.filter(**author_filters).values_list("user_id", flat=True))
                article_filters["authors__in"] = list(set(tuple(selected_users) + tuple(searched_users)))

            elif len(article_filters["authors__in"]) == 0:
                del article_filters["authors__in"]

            if len(article_filters["section__in"]) == 0:
                del article_filters["section__in"]

            max_search_results = ControlsPage.objects.first().max_search_results
            articles = ArticleInfo.objects.filter(**article_filters).distinct()[:max_search_results]

            not_found = len(articles) == 0

            return render(request, "conference/library.html", {
                "articles": [a.show_info() for a in articles],
                "form": form,
                "not_found": not_found,
                "MAX_SEARCH_RESULTS": max_search_results
            })

        return render(request, "conference/library.html", {
            "form": form,
            "not_found": True
        })
    return render(request, "conference/library.html", {
        "form": FilterArticleForm(),
        "expand_form": True
    })


@login_required
@ensure_csrf_cookie
def join_view(request):
    """Страница с формой присоединения к уже зарегистированому докладу."""
    sections = Section.objects.filter(open=True)
    return render(request, "conference/join.html",
                  {"sections": [s.serialize() for s in sections]})


def register_staff(request):
    """Страница с формой регистрации нового аккаунта редактора"""
    if request.method == "POST":
        email = request.POST.get("email")
        first_name = request.POST.get("first_name").strip()
        last_name = request.POST.get("last_name").strip()
        middle_name = request.POST.get("middle_name").strip()
        sections = request.POST.getlist("sections")
        is_reviewer = True if request.POST.get("is_reviewer") == "on" else False

        # Ensure password matches confirmation
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        if password != confirmation:
            return render(request, "conference/register/register_staff.html", {
                "message": "Пароли не совпадают."
            })

        # Attempt to create new user
        try:
            user = CustomUser.objects.create_staff_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                password=password,
                is_staff=True,
                is_active=False)
            user.save()
        except IntegrityError:
            return render(request, "conference/register/register_staff.html", {
                "message": "Пользователь с таким e-mail уже зарегистрирован."
            })

        try:
            sections_lst = []
            for section in sections:
                s = Section.objects.get(id=section)
                section_editor = SectionEditor.objects.create(
                    user=user,
                    section=s,
                    is_reviewer=is_reviewer
                )
                section_editor.save()
                sections_lst.append(s.content)
        except IntegrityError:
            return render(request, "conference/register/register_staff.html", {
                "message": "Возникла ошибка при добавлении выбранной секции."
            })

        token = default_token_generator.make_token(user)
        invitation_link = request.build_absolute_uri(reverse('confirm_staff', kwargs={
            "user_id": user.id,
            'token': token}))
        subject, footer, site = get_mail_context("Регистрация сотрудника")
        try:
            send_mail(
                subject=subject,
                message=f"Новая заявка на регистрацию сотрудника.\n\nФИО: {last_name} {first_name}  {middle_name}\ne-mail: {email}\nСекции: {' ; '.join(sections_lst)}\n\nДля подтверждения регистрации пользователя перейдите по ссылке ниже: {invitation_link}\n\nЭто письмо сформировано автоматически.",
                html_message=render_to_string('conference/emails/activate_staff/mail.html',
                                              {"last_name": last_name, "first_name": first_name, "middle_name": middle_name,
                                               "email": email, "sections_lst": sections_lst,
                                               "invitation_link": invitation_link}),
                from_email=DEFAULT_FROM_EMAIL,
                recipient_list=[DEFAULT_FROM_EMAIL]
            )
        except Exception:
            pass
        # login(request, user)
        return HttpResponseRedirect(reverse('wagtail_serve', args=('',)))
    return render(request, "conference/register/register_staff.html")


@login_required
def confirm_staff(request, user_id, token):
    """Обработка токена разрешающего пользователю присоединиться к докладу"""
    user = get_object_or_404(CustomUser, id=user_id)

    if default_token_generator.check_token(user, token) and request.user.is_staff:
        user.is_active = True
        user.save()
        return render(request, "conference/emails/activate_staff/callback.html", {"success": True})

    return render(request, "conference/emails/activate_staff/callback.html", {"success": False})


@login_required
def register_secondary(request):
    """Страница с формой добавления нового аккаунта автора."""
    registration_open = HomePage.objects.first().registration_open
    if not registration_open:
        return HttpResponseRedirect(reverse('wagtail_serve', args=('',)))

    if request.method == "POST":
        if AuthorInfo.objects.filter(user=request.user).exists():
            return render(request, "conference/register/register_secondary.html", {
                "message": "Вы ранее уже указали дополнительную информацию. "
                           "Изменить информацию о себе вы можете в своем личном кабинете."
            })

        first_name_translation = request.POST.get("first_name_translation").strip().capitalize()
        last_name_translation = request.POST.get("last_name_translation").strip().capitalize()
        country = request.POST.get("country").strip()
        city = request.POST.get("city").strip()
        institution = request.POST.get("institution").strip()
        department = request.POST.get("department").strip()
        department_group = request.POST.get("department_group").strip()
        major = request.POST.get("major").strip()
        level = request.POST.get("level")
        education_group = request.POST.get("education_group").strip()

        # ВАЛИДАЦИЯ
        if country.lower() == "рф" or country.lower() == "российская федерация":
            country = "Россия"
        if len(city) > 0:
            city = city[0].upper() + city[1:]
        if len(institution) > 0:
            if institution.lower() == "дальневосточный федеральный университет":
                institution = "ДВФУ"
            else:
                institution = institution[0].upper() + institution[1:]

        course = int(request.POST.get("course"))
        if course == '' or course > EDUCATION_LEVELS.get(request.POST.get("level"), 0):
            course = None

        try:
            author = AuthorInfo.objects.create(
                user=request.user,
                first_name_translation=first_name_translation,
                last_name_translation=last_name_translation,
                country=country,
                city=city,
                institution=institution,
                department=department,
                department_group=department_group,
                major=major,
                level=level,
                course=course,
                education_group=education_group)
            author.save()
        except IntegrityError:
            return render(request, "conference/register/register_secondary.html", {
                "message": "Произошла непредвиденная ошибка. Вы можете пропустьть этот шаг и указать информацию позже в своём личном кабинете."
            })
        return HttpResponseRedirect(reverse("third"))
    else:
        if AuthorInfo.objects.filter(user=request.user).exists():
            return HttpResponseRedirect(reverse("profile"))
        return render(request, "conference/register/register_secondary.html",
                      {"education": EDUCATION_LEVELS.keys()})


@login_required
def comment(request, article_id):
    """Добавление комментария к статье"""
    if request.method != 'POST' or not request.user.is_staff:
        return HttpResponseRedirect(reverse("article", args=(article_id,)))

    try:
        form = CommentAttachmentForm(request.POST, request.FILES)
        if form.is_valid():
            text = form.cleaned_data["text"]
            files = form.cleaned_data["files"]

            article = ArticleInfo.objects.filter(id=article_id).first()
            editor = SectionEditor.objects.filter(user=request.user.id).first()
            comment = Comment.objects.create(
                article_id=article.id,
                editor_id=editor.id,
                content=text
            )

            attachments = []
            for file in files:
                attachment = CommentAttachment.objects.create(
                    comment=comment,
                    file=file
                )
                path_tuple = os.path.split(os.path.join(MEDIA_ROOT, str(attachment.file)))
                attachments.append(os.path.join(*path_tuple))

            invitation_link = request.build_absolute_uri(reverse('article', kwargs={"article_id": article_id}))

            recipients = CustomUser.objects.filter(id__in=article.authors.all()).values_list('email', flat=True)
            subject, footer, site = get_mail_context("Сообщение от редакторской коллегии")
            send_mail_attachments(
                subject=subject,
                message=f"Здравствуйте!\n\nРедакторская коллегия оставила комментарий к вашему докладу «{article.title}»:\n\n{text}\n\nВы можете отредакрировать указанную информацию на странце доклада: {invitation_link}\n\n{footer}",
                html_message=render_to_string('conference/emails/add_comment.html',
                                              {"title": article.title, "content": text,
                                               "invitation_link": invitation_link, 'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients,
                attachments_list=attachments
            )
    except Exception as e:
        print(e)
    finally:
        return HttpResponseRedirect(reverse("article", args=(article_id,)))


@login_required
@ensure_csrf_cookie
def register_third(request):
    """Страница с формой добавления нового доклада."""
    sections = Section.objects.filter(open=True)
    keyword_length = ControlsPage.objects.first().keyword_length
    return render(request, "conference/register/register_third.html",
                  {"sections": [s.serialize() for s in sections],
                   "KEYWORDS_MAX_NUM": keyword_length})


@login_required
def edit_authorship(request, article_id):
    """Страница с формой добавления / открепления авторов от статьи."""
    article = ArticleInfo.objects.filter(id=article_id).first()
    if article is None:
        raise Http404("Доклад не найден")

    users = CustomUser.objects.filter(id__in=article.authors.all())
    authors_ids = [user.id for user in users]

    if request.user.id not in authors_ids:
        raise Http404("У вас нет доступа для редактирования данного доклада")

    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            added_user = CustomUser.objects.filter(id=data.get("user_id")).first()
            token = default_token_generator.make_token(request.user)

            invitation_link = request.build_absolute_uri(reverse('accept_invitation', kwargs={
                "sender_id": request.user.id,
                "recipient_id": added_user.id,
                "article_id": article.id,
                'token': token}))

            subject, footer, site = get_mail_context("Приглашение присоединиться к докладу")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nВам отправлено приглашение присоединиться в качестве соавтора к докладу «{article.title}» в секции «{article.section.content}». Чтобы принять приглашение, перейдите по ссылке ниже: {invitation_link}\n\n{footer}",
                html_message=render_to_string('conference/emails/invite_to_article/mail.html',
                                              {"title": article.title, "section": article.section.content,
                                               "invitation_link": invitation_link, 'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=[added_user.email]
                )
            # article.authors.add(added_user)
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": "Произошла непредвиденная ошибка. Попробуйте ещё раз позже."})

    if request.method == "DELETE":
        try:
            data = json.loads(request.body)
            deleted_user = CustomUser.objects.filter(id=data.get("user_id")).first()
            article.authors.remove(deleted_user)
            subject, footer, site = get_mail_context("Удаление из списка авторов")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nИнформируем, что вы были удалены из списка авторов доклада «{article.title}» другим его автором.\n\n{footer}",
                html_message=render_to_string('conference/emails/deleted_from_article.html',
                                              {'title': article.title,
                                               'profile_url': request.build_absolute_uri(reverse('profile')),
                                               'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=[deleted_user.email]
            )
            return JsonResponse({"success": True})
        except Exception as e:
            print(e)
            return JsonResponse({"success": False, "error": "Произошла непредвиденная ошибка. Попробуйте ещё раз позже."})

    return render(request, "conference/edit_authorship.html",
                  {"article": article.serialize(),
                   "authors": [user.serialize() for user in users],
                   "authors_ids": authors_ids})


@login_required
def accept_invitation(request, sender_id, recipient_id, article_id, token):
    """Обработка токена разрешающего пользователю присоединиться к докладу"""
    sender = get_object_or_404(CustomUser, id=sender_id)
    article = get_object_or_404(ArticleInfo, id=article_id)

    context = {
        "success": False,
        "title": article.title,
        "article_id": article.id
    }

    if default_token_generator.check_token(sender, token) and sender in article.authors.all() and request.user.id == recipient_id:
        article.authors.add(request.user)
        article.save()
        context["success"] = True
        return render(request, "conference/emails/invite_to_article/callback.html", context)

    return render(request, "conference/emails/invite_to_article/callback.html", context)


def login_view(request):
    """Страница с формой для входа в аккаунт с помощью e-mail и пароля. Общая для всех аккаунтов."""
    if request.method == "POST":

        username = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('wagtail_serve', args=('',)))
        else:
            return render(request, "conference/login.html", {
                "message": "Неверный e-mail или пароль."
            })
    else:
        return render(request, "conference/login.html")


def logout_view(request):
    """Представление для выхода из текущего аккаунт, если такой есть. Общее для всех."""
    logout(request)
    return HttpResponseRedirect(reverse('wagtail_serve', args=('',)))


def register(request):
    """Страница с формой регистрации нового аккаунта автора."""
    registration_open = HomePage.objects.first().registration_open
    if not registration_open:
        return HttpResponseRedirect(reverse('wagtail_serve', args=('',)))

    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("logout"))

    if request.method == "POST":

        if request.POST.get("consent") != "on":
            return render(request, "conference/register/register.html", {
                "message": "Для участия вв конференции необходимо дать согласие на обработку персональных данных."
            })

        email = request.POST.get("email").strip()
        first_name = request.POST.get("first_name").strip().capitalize()
        last_name = request.POST.get("last_name").strip().capitalize()
        middle_name = request.POST.get("middle_name").strip().capitalize()


        # Ensure password matches confirmation
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        if password != confirmation:
            return render(request, "conference/register/register.html", {
                "message": "Пароли не совпадают."
            })

        # Attempt to create new user
        try:
            user = CustomUser.objects.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                password=password,
                is_consent_send=True,
                is_verified=True
            )
        except IntegrityError:
            return render(request, "conference/register/register.html", {
                "message": "Пользователь с таким e-mail уже зарегистрирован."
            })
        # Временно отключим поддверждение почты, чтобы Яндекс на спам не жаловался
        # subject, footer, site = get_mail_context("Подтверждение адреса электронной почты")
        # send_email(user, context={'footer': footer, 'site': site})
        login(request, user)
        return HttpResponseRedirect(reverse("secondary"))
    else:
        return render(request, "conference/register/register.html")


@login_required()
def email_change(request):
    if request.method == 'POST':
        form = EmailChangeForm(request.user, request.POST)
        if form.is_valid():
            if CustomUser.objects.filter(email=form.cleaned_data.get('new_email1')).exists():
                return render(request, "conference/email_change/email_change.html",
                              {"form": form, "error2": "Данный e-mail уже занят."})
            form.save()
            request.user.is_verified = False
            request.user.save()
            return HttpResponseRedirect(reverse("profile"))

        errors = form.errors.as_data()
        error1 = errors.get('new_email1')
        error2 = errors.get('new_email2')
        if error1:
            error1 = error1[0].message
        if error2:
            error2 = error2[0].message

        return render(request, "conference/email_change/email_change.html", {"form": form, "error1": error1, "error2": error2})
    else:
        form = EmailChangeForm(request.user)
        return render(request, "conference/email_change/email_change.html", {"form": form})


def get_text(request, article_id):
    """API для получения текста статьи"""
    if request.method == 'GET':
        article = ArticleInfo.objects.filter(id=article_id).first()
        if article is None:
            return JsonResponse({'errors': ['Доклад не найден'], 'success': False})
        return JsonResponse({'text': "article.text", 'success': True})
    return JsonResponse({'errors': ['В настоящий момент эта функция недоступна.'], 'success': False})


def edit_general_info(request):
    """API изменения ФИО пользователя"""
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'errors': ['Для изменения данных вы должны войти в свой аккаун.'],
                                 'success': False})
        data = json.loads(request.body)

        try:
            user = CustomUser.objects.filter(id=request.user.id).first()
            user.first_name = data.get("first_name").strip().capitalize()
            user.last_name = data.get("last_name").strip().capitalize()
            user.middle_name = data.get("middle_name").strip().capitalize()
            user.save()
        except Exception as e:
            print(e)
            return JsonResponse({'errors': ['Произошла ошибка. Попробуйте снова.'], 'success': False})
        return JsonResponse({'user': user.serialize(), 'success': True})
    return JsonResponse({'errors': ['В настоящий момент эта функция недоступна.'], 'success': False})


def edit_secondary_info(request):
    """API изменения / добавления данных об авторе"""
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'errors': ['Для изменения данных вы должны войти в свой аккаун.'],
                                 'success': False})
        data = json.loads(request.body)

        try:
            user = CustomUser.objects.filter(id=request.user.id).first()
            if AuthorInfo.objects.filter(user_id=user.id).exists():
                author = AuthorInfo.objects.filter(user_id=user.id).first()
            else:
                author = AuthorInfo.objects.create(user_id=user.id)

            first_name_translation = data.get("edit_first_name_translation").strip().capitalize()
            last_name_translation = data.get("edit_last_name_translation").strip().capitalize()
            country = data.get("edit_country").strip()
            city = data.get("edit_city").strip()
            institution = data.get("edit_institution").strip()
            department = data.get("edit_department").strip()
            department_group = data.get("edit_department_group").strip()
            major = data.get("edit_major").strip()
            level = data.get("edit_level")
            education_group = data.get("edit_education_group")

            # ВАЛИДАЦИЯ
            if country.lower() == "рф" or country.lower() == "российская федерация":
                country = "Россия"
            if len(city) > 0:
                city = city[0].upper() + city[1:]
            if len(institution) > 0:
                if institution.lower() == "дальневосточный федеральный университет":
                    institution = "ДВФУ"
                else:
                    institution = institution[0].upper() + institution[1:]

            author.first_name_translation = first_name_translation
            author.last_name_translation = last_name_translation
            author.country = country
            author.city = city
            author.institution = institution
            author.department = department
            author.department_group = department_group
            author.major = major
            author.level = level
            author.education_group = education_group

            course = int(data.get("edit_course"))
            if course == '' or course > EDUCATION_LEVELS.get(data.get("edit_level"), 0):
                course = None
            author.course = course

            author.save()
        except Exception as e:
            print(e)
            return JsonResponse({'errors': ['Произошла ошибка. Попробуйте снова.'], 'success': False})
        return JsonResponse({'user': author.serialize(), 'success': True})
    return JsonResponse({'errors': ['В настоящий момент эта функция недоступна.'], 'success': False})


def edit_section_info(request):
    """API изменения прикрепённой за редактором секции"""
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'errors': ['Для изменения данных вы должны войти в свой аккаун.'],
                                 'success': False})
        if not request.user.is_staff:
            return JsonResponse({'errors': ['Для изменения данных вы должны быть сотрудником.'],
                                 'success': False})
        data = json.loads(request.body)

        try:
            user = CustomUser.objects.filter(id=request.user.id).first()
            editor = SectionEditor.objects.filter(user_id=user.id).first()
            section = Section.objects.filter(id=data.get("edit_section")).first()
            editor.section = section
            editor.save()
        except Exception as e:
            print(e)
            return JsonResponse({'errors': ['Произошла ошибка. Попробуйте снова.'], 'success': False})
        return JsonResponse({'editor': editor.serialize(), 'success': True})
    return JsonResponse({'errors': ['В настоящий момент эта функция недоступна.'], 'success': False})


def edit_article_info(request):
    """API изменения прикрепённой за редактором статьи"""
    if request.method == 'PUT':
        if not request.user.is_authenticated:
            return JsonResponse({'errors': ['Для изменения данных вы должны войти в свой аккаун.'],
                                 'success': False})
        data = json.loads(request.body)
        errors = []

        if not ArticleInfo.objects.filter(id=data.get("article_id")).exists():
            return JsonResponse({'errors': ['Доклад не найден.'], 'success': False})
        try:
            article = ArticleInfo.objects.filter(id=data.get("article_id")).first()
            if not request.user.id in [user.id for user in article.authors.all()]:
                return JsonResponse({'errors': ['Вы не являетесь автором этого доклада.'], 'success': False})

            section = Section.objects.filter(id=data.get("edit_section")).first()
            if section is None:
                return JsonResponse({'errors': ['Секция не найдена.'], 'success': False})

            article.section = section

            article.adviser_first_name = data.get("edit_adviser_first_name").strip().capitalize()
            article.adviser_last_name = data.get("edit_adviser_last_name").strip().capitalize()
            article.adviser_middle_name = data.get("edit_adviser_middle_name").strip().capitalize()
            article.adviser_first_name_translation = data.get("edit_adviser_first_name_translation").strip().capitalize()
            article.adviser_last_name_translation = data.get("edit_adviser_last_name_translation").strip().capitalize()
            article.adviser_degree = data.get("edit_adviser_degree").strip().lower()
            article.academic_title = data.get("edit_academic_title").strip().lower()
            article.job_title = data.get("edit_job_title").strip().lower()
            article.adviser_job = data.get("edit_adviser_job").strip()

            title = data.get("edit_title").strip()
            title_translation = data.get("edit_title_translation").strip()
            abstract = data.get("edit_abstract")
            abstract_translation = data.get("edit_abstract_translation")
            keywords = data.get("edit_keywords").lower().strip()
            keywords_translation = data.get("edit_keywords_translation").lower().strip()
            grant = data.get("edit_grant").strip()

            # ВАЛИДАЦИЯ ОСНОВНОЙ ИНФОРМАЦИИ
            controls_page = ControlsPage.objects.first()
            title_length = controls_page.title_length
            abstract_length = controls_page.abstract_length
            keyword_length = controls_page.keyword_length

            if len(title) > title_length:
                errors.append(f'Слишком длинная тема. Максимальная длина - {title_length} символов.')
            if len(title_translation) > title_length:
                errors.append(f'Слишком длинный перевод темы. Максимальная длина - {title_length} символов.')

            if len(abstract) > abstract_length:
                errors.append(f'Слишком длинная аннотация. Максимальная длина - {abstract_length} символов.')
            if len(abstract_translation) > abstract_length:
                errors.append(
                    f'Слишком длинный перевод аннотации. Максимальная длина - {abstract_length} символов.')

            if len(keywords.split(', ')) > keyword_length:
                errors.append(f'Слишком много ключевых слов. Максимальное количество - {keyword_length}.')
            if len(keywords_translation.split(', ')) > keyword_length:
                errors.append(f'Слишком много ключевых слов. Максимальное количество - {keyword_length}.')
            if len(errors) > 0:
                errors.append('Проверьте введенные данные и попробуйте ещё раз.')
                return JsonResponse({'errors': errors, 'success': False})

            article.title = title
            article.title_translation = title_translation
            article.abstract = abstract
            article.abstract_translation = abstract_translation
            article.keywords = keywords
            article.keywords_translation = keywords_translation
            article.grant = grant
            article.save()
        except Exception as e:
            print(e)
            return JsonResponse({'errors': ['Произошла ошибка. Попробуйте снова.'], 'success': False})
        return JsonResponse({'article': article.jsonify(), 'success': True})
    return JsonResponse({'errors': ['В настоящий момент эта функция недоступна.'], 'success': False})


@login_required
def approve_article(request, article_id):
    """API подтверждения статьи."""
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('article', kwargs={"article_id": article_id}))

    article = get_object_or_404(ArticleInfo, id=article_id)
    staff = get_object_or_404(SectionEditor, user=request.user.pk)
    old_date = article.last_updated
    if staff.is_reviewer:
        article.reviewer_approved = timezone.now() if not article.reviewer_approved else None
    else:
        article.editor_approved = timezone.now() if not article.editor_approved else None
    article.last_updated = old_date
    article.save()
    return HttpResponseRedirect(reverse('article', kwargs={"article_id": article.id}))


@login_required
def reject_or_restore_article(request, article_id):
    """API отклонения и восстановления доклада."""
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('article', kwargs={"article_id": article_id}))

    cause = request.POST.get("cause")
    article = get_object_or_404(ArticleInfo, id=article_id)
    article.rejected = timezone.now() if not article.rejected else None
    article.save()

    users = CustomUser.objects.filter(id__in=article.authors.all())
    recipients_emails = [user.email for user in users]

    try:
        if article.rejected:
            subject, footer, site = get_mail_context("Ваш доклад был отклонён")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nВаш доклад «{article.title}» был отклонён редакторской коллегией «{site}» по следующей причине: {cause}\n\n{footer}",
                html_message=render_to_string('conference/emails/reject/article_rejected.html',
                                              {'title': article.title, 'cause': cause, 'site': site,
                                               'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients_emails
            )
        else:
            subject, footer, site = get_mail_context("Ваш доклад был восстановлен")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nВаш доклад «{article.title}» был восстановлен редакторской коллегией «{site}» по следующей причине: {cause}\nРедакторская подготовка доклада будет продолжена в штатном режиме.\n\n{footer}",
                html_message=render_to_string('conference/emails/reject/article_restored.html',
                                              {'title': article.title, 'cause': cause, 'site': site,
                                               'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients_emails
            )
    except Exception as e:
        pass
    return HttpResponseRedirect(reverse('article', kwargs={"article_id": article.id}))


@login_required
def user_articles(request):
    """API списка статей текущего пользователя."""
    articles = ArticleInfo.objects.filter(id=request.user.id)
    return JsonResponse([a.show_info() for a in articles])


def degree(request):
    """API со списком всех доступных научных степеней"""
    return JsonResponse({}, safe=False)


def sections(request):
    """API данных о всех секциях на конференции"""
    data = Section.objects.all()
    return JsonResponse({"sections": [d.serialize() for d in data]})


def section(request, section_id):
    """API данных выбранной секции"""
    data = Section.objects.filter(id=section_id)
    return JsonResponse(data.serialize())


def check_technical_work(request):
    """API проверка наличия запланированых на будущее технических работ.
       Если есть, то возвращает близжайшее совпадение."""
    current_date = timezone.now()
    three_days_later = current_date + timezone.timedelta(days=3)

    next_work = TechnicalWork.objects.filter(start__gt=current_date, start__lte=three_days_later).order_by('start').first()
    return JsonResponse({"success": True, "work": next_work.serialize()}) if next_work else JsonResponse({"success": False})


def find_user(request):
    """API поиска пользователя по e-mail"""
    if request.method == "POST":
        data = json.loads(request.body)
        if CustomUser.objects.filter(email=data.get("email"), is_staff=False).exists():
            user = CustomUser.objects.get(email=data.get("email"))
            if user.is_verified:
                return JsonResponse(user.serialize())
            return JsonResponse({'error': 'Пользователь найден, однако сперва он должен подтвердить свой адрес электронной почты.'})
        return JsonResponse({'error': 'Пользователь с указанным e-mail не зарегистрирован.'})
    return JsonResponse({'log': 'Неверный метод.'})


@login_required
def join_article(request):
    """API присоединения к статье"""
    if request.method == "PUT":
        data = json.loads(request.body)
        try:
            article = ArticleInfo.objects.get(id=data.get("article_id"))
            users = CustomUser.objects.filter(id__in=article.authors.all())
            recipients_emails = [user.email for user in users]

            token = default_token_generator.make_token(request.user)
            invitation_link = request.build_absolute_uri(reverse('accept_join', kwargs={
                "user_id": request.user.id,
                "article_id": article.id,
                'token': token}))
            subject, footer, site = get_mail_context("Просьба присоединиться к вашему докладу")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\n{request.user.last_name} {request.user.first_name} {request.user.middle_name} хочет присоединиться в качестве соатора к докладу «{article.title}». Если вы согласны добавить этого автора к докладу, перейдите по ссылке ниже: {invitation_link}\n\n{footer}",
                html_message=render_to_string('conference/emails/join_article/mail.html',
                                              {'user': request.user.serialize(), 'title': article.title,
                                               'invitation_link': invitation_link, 'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients_emails
            )
            return JsonResponse({'success': True})
        except IntegrityError:
            return JsonResponse({
                'success': False,
                'error': 'Произошла ошибка. Вы можете повторить попытку позже из своего личного кабинета.'})
    return JsonResponse({
        'success': False,
        'error': 'Произошла ошибка. Вы можете повторить попытку позже из своего личного кабинета.'})


def accept_join(request, user_id, article_id, token):
    """Обработка токена разрешающего пользователю присоединиться к докладу"""
    user = get_object_or_404(CustomUser, id=user_id)
    article = get_object_or_404(ArticleInfo, id=article_id)

    context = {
        "success": False,
        "user": user.serialize(),
        "title": article.title,
        "article_id": article.id
    }

    if default_token_generator.check_token(user, token) and request.user in article.authors.all():
        article.authors.add(user)
        article.save()
        context["success"] = True
        return render(request, "conference/emails/join_article/callback.html", context)

    return render(request, "conference/emails/join_article/callback.html", context)


def check_article_exists(request):
    """API проверки наличия статьи
    Если статья найдена - возвращает данные о ней.
    Иначе возвращает JSON {'result': False}"""
    if request.method == "POST":
        data = json.loads(request.body)
        section = Section.objects.get(id=data.get("section_id"))
        if ArticleInfo.objects.filter(section=section, title__iexact=data.get("title")).exists():
            article = ArticleInfo.objects.get(section=section, title__iexact=data.get("title"))
            if request.user in article.authors.all():
                return JsonResponse({'success': True, 'errors': ['У вас уже есть статья с таким названием.']})

            authors = CustomUser.objects.filter(id__in=article.authors.all())
            return JsonResponse({
                'success': True,
                'section': section.serialize(),
                'article': article.show_info(),
                'authors': [a.serialize() for a in authors]
            })
        return JsonResponse({'success': False, 'errors': ['Доклад не найден.']})
    return JsonResponse({'log': 'Неверный метод.'})


def register_article(request):
    """API регистрации новой статьи"""
    if request.method == "POST":
        data = json.loads(request.body)
        errors = []
        section = Section.objects.get(id=data.get("section_id"))
        title = data.get("title").strip()
        title_translation = data.get("title_translation").strip()
        abstract = data.get("abstract")
        abstract_translation = data.get("abstract_translation")
        keywords = data.get("keywords").lower().strip()
        keywords_translation = data.get("keywords_translation").lower().strip()
        grant = data.get("grant").strip()

        # ВАЛИДАЦИЯ ОСНОВНОЙ ИНФОРМАЦИИ
        controls_page = ControlsPage.objects.first()
        title_length = controls_page.title_length
        abstract_length = controls_page.abstract_length
        keyword_length = controls_page.keyword_length

        if len(title) > title_length:
            errors.append(f'Слишком длинная тема. Максимальная длина - {title_length} символов.')
        if len(title_translation) > title_length:
            errors.append(f'Слишком длинный перевод темы. Максимальная длина - {title_length} символов.')

        if len(abstract) > abstract_length:
            errors.append(f'Слишком длинная аннотация. Максимальная длина - {abstract_length} символов.')
        if len(abstract_translation) > abstract_length:
            errors.append(f'Слишком длинный перевод аннотации. Максимальная длина - {abstract_length} символов.')

        if len(keywords.split(', ')) > keyword_length:
            errors.append(f'Слишком много ключевых слов. Максимальное количество - {keyword_length}.')
        if len(keywords_translation.split(', ')) > keyword_length:
            errors.append(f'Слишком много ключевых слов. Максимальное количество - {keyword_length}.')

        # ИНФОРМАЦИЯ О НАУЧНОМ РУКОВОДИТЕЛЕ
        if data.get("adviser_block") == "on":
            adviser_first_name = data.get("adviser_first_name").strip().capitalize()
            adviser_last_name = data.get("adviser_last_name").strip().capitalize()
            adviser_middle_name = data.get("adviser_middle_name").strip().capitalize() if data.get("adviser_middle_name") != '' else None
            adviser_first_name_translation = data.get("adviser_first_name_translation").strip().capitalize()
            adviser_last_name_translation = data.get("adviser_last_name_translation").strip().capitalize()
            adviser_degree = data.get("adviser_degree").lower().strip()
            adviser_academic_title = data.get("academic_title").strip()
            adviser_job_title = data.get("job_title").lower().strip()
            adviser_job = data.get("adviser_job").strip()
        else:
            adviser_first_name = None
            adviser_last_name = None
            adviser_middle_name = None
            adviser_first_name_translation = None
            adviser_last_name_translation = None
            adviser_academic_title = None
            adviser_job_title = None
            adviser_degree = None
            adviser_job = None

        if len(errors) > 0:
            errors.append("Обаружены некорректно заполненые поля. Пожалуйста, исправьте ошибки указанные ошибки.")
            return JsonResponse({'errors': errors, 'success': False})

        authors = [request.user]
        recipients_emails = []
        if data.get("co_authorship") != 'off':
            for co_author in data.get("co_author_id"):
                author = CustomUser.objects.get(id=co_author)
                authors.append(author)
                recipients_emails.append(author.email)

        # Attempt to create new user
        try:
            article = ArticleInfo.objects.create(
                section=section,
                title=title,
                title_translation=title_translation,
                abstract=abstract,
                abstract_translation=abstract_translation,
                keywords=keywords,
                keywords_translation=keywords_translation,
                grant=grant,

                adviser_first_name=adviser_first_name,
                adviser_last_name=adviser_last_name,
                adviser_middle_name=adviser_middle_name,
                adviser_first_name_translation=adviser_first_name_translation,
                adviser_last_name_translation=adviser_last_name_translation,
                adviser_degree=adviser_degree,
                academic_title=adviser_academic_title,
                job_title=adviser_job_title,
                adviser_job=adviser_job
            )
            article.authors.add(*authors)
            article.save()
            subject, footer, site = get_mail_context("Добавление в качестве соавтора")
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nВы были добавлены в список авторов доклада «{title}» в секции «{section.content}».\n\n{footer}",
                html_message=render_to_string('conference/emails/added_to_article.html',
                                              {'title': title, 'section': section.content,
                                               'profile_url': request.build_absolute_uri(reverse('profile')),
                                               'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=recipients_emails
            )
        except IntegrityError as e:
            print(e)
            errors.append("Произошла непредвиденная ошибка. Вы можете пропустьть этот шаг и указать информацию позже в своём личном кабинете.")
            return JsonResponse({'errors': errors})
        return JsonResponse({'success': True})

    return JsonResponse({'log': 'Неверный метод.'})


def search_articles(request):
    editor = SectionEditor.objects.filter(user=request.user.id).values_list('section', 'is_reviewer')[0]
    filters = {"section": editor[0]}

    data = json.loads(request.body)
    if data.get('filter_all'):
        raw_data = ArticleInfo.objects.filter(**filters)
        return JsonResponse({'items': [item.get_json() for item in raw_data], "success": True})

    if data.get('filter_winners'):
        filters["is_winner"] = True

    if data.get('filter_rejected'):
        filters["rejected__isnull"] = False

    if data.get('filter_edited'):
        if editor[1]:
            raw_data = ArticleInfo.objects.filter(**filters).exclude(reviewer_approved__isnull=True)
            check_dates = [item.reviewer_approved for item in raw_data]
        else:
            raw_data = ArticleInfo.objects.filter(**filters).exclude(editor_approved__isnull=True)
            check_dates = [item.editor_approved for item in raw_data]

        outdated = []
        for i in range(len(raw_data)):
            article = raw_data[i]
            check = check_dates[i]
            users = CustomUser.objects.filter(id__in=article.authors.all()).values_list('id', "last_updated")
            authors = AuthorInfo.objects.filter(user_id__in=[u[0] for u in users]).values_list('last_updated', flat=True)
            sources = Source.objects.filter(article=article.id).values_list('last_updated', flat=True)

            last_update = [article.last_updated] + list(authors) + [u[1] for u in users] + list(sources)
            if not up_to_date(check, last_update):
                outdated.append(article)
                continue

            last_update = []
            thesis = ArticleThesis.objects.filter(article=article.id).values_list('last_updated', flat=True)
            if thesis:
                last_update.append(thesis[0])

            text = ArticleText.objects.filter(article=article.id).values_list('last_updated', flat=True)
            if text:
                last_update.append(text[0])

            if not up_to_date(check, last_update):
                outdated.append(article)
        return JsonResponse({'items': [item.get_json() for item in outdated], "success": True})

    if data.get('filter_unapproved'):
        if editor[1]:
            filters["reviewer_approved"] = None
        else:
            filters["editor_approved"] = None

    raw_data = ArticleInfo.objects.filter(**filters)
    return JsonResponse({'items': [item.get_json() for item in raw_data], "success": True})


def search_title(request):
    """API для автозавершения поиска заголовка статьи"""
    query = request.GET.get('title')
    if query:
        titles = list(ArticleInfo.objects.filter(title__istartswith=query)[:5].values_list('title', flat=True))
        return JsonResponse({
            'data': titles,
            'success': True
        })
    return JsonResponse({'success': False})


def search_title_translation(request):
    """API для автозавершения поиска заголовка статьи"""
    query = request.GET.get('title')
    if query:
        titles = list(ArticleInfo.objects.filter(title_translation__istartswith=query)[:5].values_list('title_translation', flat=True))
        return JsonResponse({
            'data': titles,
            'success': True
        })
    return JsonResponse({'success': False})


def resend_email(request):
    if request.method == 'PUT':
        if request.user.is_authenticated and not request.user.is_verified:
            subject, footer, site = get_mail_context("Подтверждение адреса электронной почты")
            print("----")
            print(f"subject: {subject}")
            print(f"footer: {footer}")
            print(f"site: {site}")
            send_email(request.user, context={'footer': footer, 'site': site})
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})


def register_instruction(request):
    return render(request, 'conference/instructions/register_instruction.html')


def thesis_instruction(request):
    return render(request, 'conference/instructions/thesis_instruction.html')


def article_instruction(request):
    return render(request, 'conference/instructions/article_instruction.html')


def staff_instruction(request):
    return render(request, 'conference/instructions/staff_instruction.html')


def upload_thesis_instruction(request):
    return render(request, 'conference/instructions/upload_thesis_instruction.html')

import os
import puremagic

from modelcluster.fields import ParentalKey

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.urls import reverse

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .managers import CustomUserManager
from .config.conference_config import *

# Validators
ext_article_files_validator = FileExtensionValidator(["docx"], _(
        "Файлы с расширением “%(extension)s” не поддерживаются. "
        "Разрешённые форматы файлов: %(allowed_extensions)s."
    ))

ext_consent_file_validator = FileExtensionValidator(["pdf"], _(
        "Файлы с расширением “%(extension)s” не поддерживаются. "
        "Разрешённые форматы файлов: %(allowed_extensions)s."
    ))


def validate_article_files_maintype(file):
    accept = ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]
    file_mime_type = puremagic.from_stream(file, mime=True)
    if file_mime_type not in accept:
        raise ValidationError("Неподдерживаемый формат файла")


def validate_consent_file_maintype(file):
    accept = ["application/pdf"]
    file_mime_type = puremagic.from_stream(file, mime=True)
    if file_mime_type not in accept:
        raise ValidationError("Неподдерживаемый формат файла")


# Models
class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False, verbose_name="Сотрудник?")
    is_active = models.BooleanField(default=True, verbose_name="Активирован?")
    is_verified = models.BooleanField(default=False, verbose_name="e-mail подверждён?")
    is_winner = models.BooleanField(default=False, verbose_name="Победитель?")

    is_consent_send = models.BooleanField(default=False, verbose_name="Согласие отправлено?")
    is_participation_confirmed = models.BooleanField(default=False, verbose_name="Участие подтверждено?")

    date_joined = models.DateTimeField(default=timezone.now, verbose_name="Дата регистрации")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    first_name = models.CharField(max_length=150, blank=False, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, blank=True, verbose_name="Отчество")
    last_name = models.CharField(max_length=150, blank=False, verbose_name="Фамилия")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}"

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "last_name": self.last_name,
            "email": self.email
        }

    @property
    def fullname(self):
        return f"{self.last_name} {self.first_name} {self.middle_name}" if self.middle_name else f"{self.last_name} {self.first_name}"

    @property
    def fullname_reverse(self):
        return f"{self.first_name} {self.middle_name} {self.last_name}" if self.middle_name else f"{self.first_name} {self.last_name}"

    @property
    def initials(self):
        return f"{self.last_name} {self.first_name[0]}.\u00A0{self.middle_name[0]}." if self.middle_name else f"{self.last_name}\u00A0{self.first_name[0]}."


class AuthorInfo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="author", verbose_name="Пользователь")

    first_name_translation = models.CharField(max_length=64, blank=True, null=True, verbose_name="Перевод имени")
    last_name_translation = models.CharField(max_length=64, blank=True, null=True, verbose_name="Перевод фамилии")

    country = models.CharField(max_length=64, default="Россия", verbose_name="Страна")
    city = models.CharField(max_length=64, default="Владивосток", verbose_name="Город")
    institution = models.TextField(default="ДВФУ", verbose_name="Учебное заведение")
    department = models.TextField(default="ШИГН", verbose_name="Подразделение")
    department_group = models.TextField(blank=True, null=True, verbose_name="Департамент")
    major = models.TextField(blank=True, null=True, verbose_name="Направление")
    level = models.CharField(max_length=24, default=DEFAULT_LEVEL, verbose_name="Уровень образования") # бакалавр, магистр, специалист...
    course = models.IntegerField(blank=True, null=True, verbose_name="Курс")
    education_group = models.TextField(blank=True, null=True, verbose_name="Учебная группа")

    is_participation_confirmed = models.BooleanField(default=False, verbose_name="Участие подтверждено?")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return f"Автор: {self.first_name_translation} {self.last_name_translation}"

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "first_name_translation": self.first_name_translation,
            "last_name_translation": self.last_name_translation,
            "country": self.country,
            "city": self.city,
            "institution": self.institution,
            "department": self.department,
            "department_group": self.department_group,
            "major": self.major,
            "level": self.level,
            "course": self.course,
            "education_group": self.education_group,
            "is_participation_confirmed": self.is_participation_confirmed
        }

    def validate_level(self):
        return self.level in EDUCATION_LEVELS.keys()

    def validate_course(self):
        if self.level in EDUCATION_LEVELS.keys():
            return 1 <= self.course <= EDUCATION_LEVELS.get(self.level)
        return True

    @property
    def address(self):
        return f"{self.department} {self.institution}, г. {self.city}" if self.department else f"{self.institution}, г. {self.city}"


class Section(models.Model):
    content = models.TextField(blank=False, verbose_name="Заглавие")
    open = models.BooleanField(default=True, verbose_name="Регистрация открыта?")

    def __str__(self):
        # res = "Регистрация открыта: " if self.open else "Регистрация закрыта: "
        return self.content

    class Meta:
        verbose_name = "Секция"
        verbose_name_plural = "Секции"
        ordering = ["content"]

    def serialize(self):
        return {
            "id": self.id,
            "open": self.open,
            "content": self.content
        }


class SectionEditor(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="editor", verbose_name="Пользователь")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="working_section", verbose_name="Секция")
    confirmed = models.BooleanField(default=False, verbose_name="Проверен?")
    is_reviewer = models.BooleanField(default=False, verbose_name="Резензент")

    def __str__(self):
        return f"{self.user}"

    class Meta:
        verbose_name = "Редактор"
        verbose_name_plural = "Редакторы"

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.id,
            "section": str(self.section),
        }


class ArticleInfo(models.Model):
    authors = models.ManyToManyField(CustomUser, verbose_name="Авторы")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="related_section", verbose_name="Секция")

    adviser_first_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Имя научрука")
    adviser_middle_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Отчество научрука")
    adviser_last_name = models.CharField(max_length=64, blank=True, null=True, verbose_name="Фамилия научрука")
    adviser_first_name_translation = models.CharField(max_length=64, blank=True, null=True, verbose_name="Перевод имени научрука")
    adviser_last_name_translation = models.CharField(max_length=64, blank=True, null=True, verbose_name="Перевод фамилии научрука")
    adviser_degree = models.CharField(max_length=128, blank=True, null=True, verbose_name="Ученая степень")
    academic_title = models.CharField(max_length=128, blank=True, null=True, verbose_name="Ученое звание")
    job_title = models.CharField(max_length=128, blank=True, null=True, verbose_name="Должность")
    adviser_job = models.TextField(blank=True, null=True, verbose_name="Место работы")

    title = models.TextField(blank=False, verbose_name="Тема")
    title_translation = models.TextField(blank=False, verbose_name="Перевод темы")
    abstract = models.TextField(max_length=ABSTRACT_MAX_LENGTH, blank=False, verbose_name="Аннотация")
    abstract_translation = models.TextField(max_length=ABSTRACT_MAX_LENGTH, blank=False, verbose_name="Перевод аннотации")
    keywords = models.TextField(blank=False, verbose_name="Ключевые слова")  # [str.split(',').strip().rstrip()]
    keywords_translation = models.TextField(blank=False, verbose_name="Перевод ключевых слов")  # [str.split(',').strip().rstrip()]
    grant = models.TextField(blank=True, null=True, verbose_name="Работа по гранту")

    is_complete = models.BooleanField(default=False, verbose_name="Принята к публикации?")
    is_winner = models.BooleanField(default=False, verbose_name="Победитель?")
    deadline = models.DateField(default=REGISTRATION_CLOSE_DATETIME, verbose_name="Дедлайн для изменения информации")
    rejected = models.DateTimeField(blank=True, null=True, verbose_name="Отклонён")

    # last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")
    last_updated = models.DateTimeField(auto_now_add=True, verbose_name="Последнее обновление")
    editor_approved = models.DateTimeField(blank=True, null=True, verbose_name="Проверено редактором")
    reviewer_approved = models.DateTimeField(blank=True, null=True, verbose_name="Проверено рецензентом")

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = "Доклад"
        verbose_name_plural = "Доклады"

    def get_absolute_url(self):
        return reverse("article", kwargs={"article_id": self.id})

    def serialize(self):
        return {
            "id": self.id,
            "authors": self.authors,
            "section": self.section,
            "adviser_first_name": self.adviser_first_name,
            "adviser_middle_name": self.adviser_middle_name,
            "adviser_last_name": self.adviser_last_name,
            "adviser_first_name_translation": self.adviser_first_name_translation,
            "adviser_last_name_translation": self.adviser_last_name_translation,
            "adviser_degree": self.adviser_degree,
            "academic_title": self.academic_title,
            "job_title": self.job_title,
            "adviser_job": self.adviser_job,
            "title": self.title,
            "title_translation": self.title_translation,
            "abstract": self.abstract,
            "abstract_translation": self.abstract_translation,
            "keywords": self.keywords,
            "keywords_translation": self.keywords_translation,
            "grant": self.grant,
            "complete": self.is_complete,
            'is_winner': self.is_winner,
            'editor_approved': self.editor_approved,
            'reviewer_approved': self.reviewer_approved,
            'rejected': self.rejected
        }

    def jsonify(self):
        return {
            "id": self.id,
            "section": str(self.section),
            "section_id": self.section.id,
            "adviser_first_name": self.adviser_first_name,
            "adviser_middle_name": self.adviser_middle_name,
            "adviser_last_name": self.adviser_last_name,
            "adviser_first_name_translation": self.adviser_first_name_translation,
            "adviser_last_name_translation": self.adviser_last_name_translation,
            "adviser_degree": self.adviser_degree,
            "academic_title": self.academic_title,
            "job_title": self.job_title,
            "adviser_job": self.adviser_job,
            "title": self.title,
            "title_translation": self.title_translation,
            "abstract": self.abstract,
            "abstract_translation": self.abstract_translation,
            "keywords": self.keywords,
            "keywords_translation": self.keywords_translation,
            "grant": self.grant,
            "complete": self.is_complete,
            'is_winner': self.is_winner,
            'editor_approved': self.editor_approved,
            'reviewer_approved': self.reviewer_approved,
            'rejected': self.rejected
        }

    def show_info(self):
        return {
            "id": self.id,
            "title": self.title,
            "section": str(self.section),
            "keywords": self.keywords,
            "complete": self.is_complete,
            'is_winner': self.is_winner,
            'deadline': self.deadline,
            'rejected': self.rejected
        }

    def get_json(self):
        return {
            "id": self.id,
            "url": self.get_absolute_url(),
            "title": self.title,
            "section": str(self.section),
            "keywords": self.keywords,
            'is_winner': self.is_winner,
            'editor_approved': self.editor_approved,
            'reviewer_approved': self.reviewer_approved,
            'thesis_loaded': ArticleThesis.objects.filter(article=self.id).exists(),
            'text_loaded': ArticleText.objects.filter(article=self.id).exists(),
            'rejected': self.rejected
        }

    def validate(self):
        return len(self.keywords[:].split(',')) <= KEYWORDS_MAX_NUM

    @property
    def fullname(self):
        if self.adviser_first_name and self.adviser_last_name:
            return f"{self.adviser_last_name} {self.adviser_first_name} {self.adviser_middle_name}" if self.adviser_middle_name else f"{self.adviser_last_name} {self.adviser_first_name}"
        return "Не указан"

    @property
    def adviser_initials(self):
        if self.adviser_first_name and self.adviser_last_name:
            return f"{self.adviser_last_name} {self.adviser_first_name[0]}.\u00A0{self.adviser_middle_name[0]}." if self.adviser_middle_name else f"{self.adviser_last_name}\u00A0{self.adviser_first_name[0]}."
        return "Не указан"

    @property
    def adviser_title(self):
        if self.adviser_first_name and self.adviser_last_name:
            academic_title = self.academic_title if self.academic_title else "ученое звание отсутствует"

            if self.job_title and self.adviser_job:
                job_string = f"{self.job_title} {self.adviser_job}"
            elif self.adviser_job:
                job_string = self.adviser_job
            elif self.job_title:
                job_string = self.job_title
            else:
                job_string = None

            tun_text = f"{self.adviser_degree}, {academic_title}, {job_string}" if job_string else f"{self.adviser_degree}, {academic_title}"
            return tun_text
        return "Не указан"

    @property
    def adviser_info(self):
        return [self.adviser_initials, self.adviser_title]


@receiver(pre_save, sender=ArticleInfo)
def update_last_updated(sender, instance, **kwargs):
    if not instance.pk:
        instance.last_updated = timezone.now()
    else:
        changed_fields = instance._state.fields_cache
        if any(field != 'editor_approved' and field != 'reviewer_approved' for field in changed_fields.keys() if field not in ['editor_approved', 'reviewer_approved']):
            instance.last_updated = timezone.now()


class ArticleText(models.Model):
    article = models.ForeignKey(ArticleInfo, on_delete=models.CASCADE, related_name="related_text", verbose_name="Доклад")
    file = models.FileField(upload_to="articles/", blank=True, null=True, validators=[
        ext_article_files_validator, validate_article_files_maintype], verbose_name="Текст статьи")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"Материалы: {self.article}"

    class Meta:
        verbose_name = "Текст статьи"
        verbose_name_plural = "Тексты статей"

    def delete(self):
        self.file.delete()
        super().delete()

    def serialize(self):
        return {
            "id": self.id,
            "article": self.article,
            "file": self.file,
            "filename": self.filename
        }

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class ArticleThesis(models.Model):
    article = models.ForeignKey(ArticleInfo, on_delete=models.CASCADE, related_name="related_thesis", verbose_name="Доклад")
    file = models.FileField(upload_to="theses/", blank=True, null=True, validators=[
        ext_article_files_validator, validate_article_files_maintype], verbose_name="Тезисы доклада")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Дата загрузки")

    def __str__(self):
        return f"Тезисы: {self.article}"

    class Meta:
        verbose_name = "Тезисы"
        verbose_name_plural = "Тезисы"

    def delete(self):
        self.file.delete()
        super().delete()

    def serialize(self):
        return {
            "id": self.id,
            "article": self.article,
            "file": self.file,
            "filename": self.filename
        }

    @property
    def filename(self):
        return f"{os.path.basename(self.file.name)[:35]}..."


class Comment(models.Model):
    article = models.ForeignKey(ArticleInfo, on_delete=models.CASCADE, related_name="related_comment", verbose_name="Доклад")
    editor = models.ForeignKey(SectionEditor, on_delete=models.CASCADE, related_name="related_comment", verbose_name="Редактор")

    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    content = models.TextField(blank=False, verbose_name="Текст комментария")

    def __str__(self):
        return f"Комментарий от {self.editor} на статью {self.article}"

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-creation_date"]

    def serialize(self):
        return {
            "id": self.id,
            "article": self.article,
            "editor": str(self.editor),
            "creation_date": self.creation_date,
            "content": self.content
        }

    def map_attachments(self):
        attachments_raw = CommentAttachment.objects.filter(comment=self.id)
        return {"comment": self.serialize(), "attachments": [item.serialize() for item in attachments_raw]}


class CommentAttachment(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="related_comment", verbose_name="Комментарий")
    file = models.FileField(upload_to='comments/')

    class Meta:
        verbose_name = "Вложение к комментарию"
        verbose_name_plural = "Вложения к комментариям"

    def delete(self):
        self.file.delete()
        super().delete()

    def serialize(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "file": self.file,
            "filename": self.filename
        }

    @property
    def filename(self):
        return f"{os.path.basename(self.file.name)[:35]}..."

    def __str__(self):
        return os.path.basename(self.file.name)


class Source(models.Model):
    article = models.ForeignKey(ArticleInfo, on_delete=models.CASCADE, related_name="related_source", verbose_name="Доклад")
    content = models.TextField(blank=False, verbose_name="Библиографическая запись")
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "Научный источник"
        verbose_name_plural = "Научные источники"

    def serialize(self):
        return {
            "id": self.id,
            "article": self.article.id,
            "content": self.content
        }


class Consent(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="related_consent", verbose_name="Пользователь")
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    file = models.FileField(upload_to="consents/", blank=True, null=True, validators=[
        ext_consent_file_validator, validate_consent_file_maintype], verbose_name="Загруженый файл")

    def __str__(self):
        return f"Согласие от {str(self.user)}"

    class Meta:
        verbose_name = "Согласие на обработку персональных данных"
        verbose_name_plural = "Согласия"
        ordering = ["-creation_date"]

    def serialize(self):
        return {
            "id": self.id,
            "user": str(self.user),
            "creation_date": self.creation_date,
            "file": self.file
        }

    def delete(self):
        self.file.delete()
        super().delete()

    @property
    def filename(self):
        return os.path.basename(self.file.name)


class TechnicalWork(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    start = models.DateTimeField(verbose_name="Начало работы")
    end = models.DateTimeField(verbose_name="Окончание работы")

    def __str__(self):
        return f"Технические работы c {self.start} до {self.end}"

    class Meta:
        verbose_name = "Техническое обслуживание"
        verbose_name_plural = "Технические работы"
        ordering = ["-creation_date"]

    def serialize(self):
        return {
            "id": self.id,
            "start": self.start,
            "end": self.end
        }

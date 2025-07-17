from django.db import models

from wagtail.blocks import StructBlock, CharBlock, RichTextBlock, DateBlock, BooleanBlock, URLBlock, EmailBlock, \
    ListBlock, TextBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from modelcluster.fields import ParentalKey


class HomeHeaderBlock(StructBlock):
    sponsor = CharBlock(null=True, blank=True, help_text="Минобр и др.",
                        verbose_name="Спонсор")
    title = CharBlock(null=True, blank=True, help_text="Статус учреждения, проводящего конференцию",
                      verbose_name="Статус")
    place = RichTextBlock(null=True, blank=True, help_text="Название учреждения, проводящего конференцию",
                          verbose_name="Название учреждения")

    introduction = RichTextBlock(null=True, blank=True, help_text="Обращение к авторам",
                                 verbose_name="Вступление")
    conference_name = RichTextBlock(null=True, blank=True, help_text="Полное название конференции",
                                    verbose_name="Название конференции")

    class Meta:
        icon = 'clipboard-list'
        template = 'blocks/home_header_block.html'


class HomeBaseInfoBlock(StructBlock):
    date = DateBlock(
        null=True, blank=True, help_text="Дата проведения конференции",
        verbose_name="Дата проведения конференции", required=False,
        # format="%d %B %Y"
    )

    address = CharBlock(null=True, blank=True, help_text="Адрес места проведения конференции",
                        verbose_name="Адрес", required=False)

    language = CharBlock(null=True, blank=True, help_text="Рабочий язык",
                         verbose_name="Рабочий язык", required=False)

    participation = CharBlock(null=True, blank=True, help_text="Форма участия",
                              verbose_name="Форма участия", required=False)

    class Meta:
        icon = 'bars'
        template = 'blocks/home_base_info_block.html'


class DoubleImageBlock(StructBlock):
    left = ImageChooserBlock(null=True, blank=True, help_text="Изображение слева",
                             verbose_name="Изображение слева")
    right = ImageChooserBlock(null=True, blank=True, help_text="Изображение справа",
                              verbose_name="Изображение справа")

    class Meta:
        icon = 'image'
        template = 'blocks/double_image_block.html'


class HomeControlsBlock(StructBlock):

    program = DocumentChooserBlock(
        null=True, blank=True,
        required=False,
        on_delete=models.SET_NULL,
        help_text='Программа конференции, отображаемая на главной странице',
    )

    instruction_url = URLBlock(
        null=True, blank=True,
        required=False,
        help_text='Ссылка на страницу с одной из инструкций к докладам. Если не указана, то используется инструкция для тезисов',
    )

    class Meta:
        icon = 'bars'
        template = 'blocks/home_controls_block.html'


class FooterBlock(StructBlock):

    qr_code = ImageChooserBlock(
        null=True, blank=True,
        required=False,
        help_text='QR-код ведущий на сайт организации. Отобразится внизу страницы по левому краю',
        verbose_name='QR-код',
    )

    qr_link = URLBlock(
        null=True, blank=True,
        required=False,
        help_text='Ссылка заключённая в QR-коде',
        verbose_name='Ссылка заключённая в QR-коде',
    )

    contact_information = RichTextBlock(
        blank=True, null=True,
        verbose_name='Контактная информация',
        help_text='Контактная информация. Отобразится внизу страницы по правому краю',
    )

    class Meta:
        icon = 'clipboard-list'
        template = 'blocks/footer_block.html'


class ReleaseDataBlock(StructBlock):
    organisation = CharBlock(max_length=255, required=False, blank=True, null=True,
                             verbouse_name='Организация проводящая конференцию',
                             help_text="Организация проводящая конференцию")
    post_code = CharBlock(max_length=32, required=False, blank=True, null=True,
                          verbouse_name='Почтовый индекс', help_text="Почтовый индекс")
    address = CharBlock(blank=True, null=True, required=False,
                        verbouse_name='Адрес организации', help_text="Адрес организации")
    email = EmailBlock(blank=True, null=True, required=False,
                       verbouse_name='Контактный E-mail', help_text="Контактный E-mail")
    phone = CharBlock(blank=True, null=True, required=False,
                      verbouse_name='Контактный телефон', help_text="Контактный телефон")
    copyrite_text = CharBlock(blank=True, null=True, required=False,
                              verbouse_name='Копирайт', help_text="Копирайт")

    class Meta:
        icon = 'clipboard-list'


class EditorBlock(StructBlock):

    name = CharBlock(verbose_name='ФИО', help_text="ФИО (в формате: «И. О. Фамилия»)")
    position = CharBlock(requiqed=False, null=True, blank=True,
                         verbose_name='Учёное знание', help_text='Учёное знание (сокращённо). Если должнось отсутствует, оставьте прочерк ("-")')

    class Meta:
        icon = 'user'


class CollectionImprintBlock(StructBlock):

    udk = CharBlock(max_length=32, blank=True, null=True, required=False, verbose_name='УДК', help_text="УДК")
    bbk = CharBlock(max_length=32, blank=True, null=True, required=False, verbose_name='ББК', help_text="ББК")
    isbn = CharBlock(max_length=32, blank=True, null=True, required=False, verbose_name='ISBN', help_text="ISBN")

    conference_date = DateBlock(blank=True, null=True, required=False,
                                verbose_name='Дата проведения конференции', help_text="Дата проведения конференции")
    publication_date = DateBlock(blank=True, null=True, required=False,
                                 verbose_name='Дата публикации', help_text="Дата публикации")

    title = CharBlock(max_length=255, blank=True, null=True, required=False,
                      verbose_name='Заглавие издания', help_text="Заглавие издания")
    description = CharBlock(max_length=255, blank=True, null=True, required=False,
                            verbose_name='Краткое писание', help_text="Краткое описание издания")
    city = CharBlock(max_length=128, blank=True, null=True, required=False,
                     verbose_name='Город проведения конференции', help_text="Город проведения конференции")

    publishing_place = CharBlock(max_length=255, blank=True, null=True, required=False,
                                 verbose_name="Издательство", help_text="Издательство")
    publishing_city = CharBlock(max_length=255, blank=True, null=True, required=False,
                                verbose_name='Город, в котором находится издательство',
                                help_text="Город, в котором находится издательство")

    url = models.URLField(blank=True, null=True, verbose_name='Ссылка на публикацию')

    release = ReleaseDataBlock(blank=True, null=True, required=False,
                               verbose_name="Выпускные данные", help_text="Выпускные данные")

    annotation = TextBlock(blank=True, null=True, required=False,
                           verbose_name="Аннотация", help_text="Аннотация")

    class Meta:
        icon = 'clipboard-list'

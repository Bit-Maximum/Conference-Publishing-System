from datetime import datetime

from django.db import models
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from wagtail.documents.blocks import DocumentChooserBlock

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import StreamField, RichTextField
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.blocks import RichTextBlock, RawHTMLBlock, CharBlock, ListBlock
from wagtail.contrib.table_block.blocks import TableBlock

from mailings.config.mailings_config import MailTemplateCode, mail_template_choices
from .blocks import HomeHeaderBlock, HomeBaseInfoBlock, DoubleImageBlock, HomeControlsBlock, CollectionImprintBlock, \
    EditorBlock
from .snippets import Footer


class HomePage(Page):

    subpage_types = ['cms.InstructionsIndexPage', 'cms.ControlsPage', 'cms.BaseMailPage']
    max_count = 1

    registration_open = models.BooleanField(
        default=True,
        verbose_name='Регистрация открыта?',
        help_text='Открыть регистрацию',
    )

    controls = StreamField([
        ("home_controls", HomeControlsBlock(label='Стандартная панель')),
    ], block_counts={"home_controls": {'min_num': 1, 'max_num': 1}},
       help_text='Управление домашней страницей', verbose_name='Панель управления', blank=True, null=True)

    header_images = StreamField([
        ("double_image", DoubleImageBlock(label='Два изображения')),
        ('image', ImageChooserBlock(label='Одно изображение')),
    ], blank=True,
       verbose_name='Изображения в шапке пригласительного письма')

    header = StreamField([
        ("home_header", HomeHeaderBlock(label='Заполнить шаблон')),
        ('header_text', RichTextBlock(
            features=['bold', 'italic', 'h2', 'h3', 'h4', 'hr', 'link', 'ol', 'ul', ],
            label='Текст'))],
        blank=True,
        verbose_name='Шапка пригласительного письма')

    base_info = StreamField([
        ("home_base_info", HomeBaseInfoBlock(label='Заполнить шаблон')),
        ('base_info_text', RichTextBlock(
            features=['bold', 'italic', 'h2', 'h3', 'h4', 'hr', 'link', 'ol', 'ul', ],
            label='Текст'))],
        blank=True,
        verbose_name='Базовая информация')

    body = StreamField(
        [
            ('image', ImageChooserBlock(label='Изображение')),
            ('html', RawHTMLBlock(label='Сторонний виджет')),
            ('sections', TableBlock(label='Открытые секции', template='blocks/opened_sections_block.html')),
            ('text', RichTextBlock(
                features=['bold', 'italic', 'h2', 'h3', 'h4', 'hr', 'link', 'ol', 'ul', ],
                label='Текст')),
        ],
        blank=True,
        verbose_name='Контент',
    )

    finisher = RichTextField(
        blank=True,
        null=True,
        verbose_name='Завершающий блок',
        help_text='Текст отобразится внизу страницы по правому краю',
    )

    class Meta:
        verbose_name = 'Домашняя страница'
        verbose_name_plural = 'Домашние страницы'

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('registration_open'),

            FieldPanel('controls'),
        ], heading="Панель управления", help_text="Управление домашней страницей"),
        FieldPanel('header_images'),
        FieldPanel('header'),
        FieldPanel('base_info'),
        FieldPanel('body'),
        FieldPanel('finisher'),
    ]


class InstructionsIndexPage(Page):

    subpage_types = ['cms.InstructionPage']
    parent_page_types = ['cms.HomePage']
    max_count = 1

    class Meta:
        verbose_name = 'Раздел «Инструкции»'
        verbose_name_plural = 'Разделы «Инструкции»'


class InstructionPage(Page):

    subpage_types = []
    parent_page_types = ['cms.InstructionsIndexPage']

    subtitle = models.CharField(
        blank=True, null=True,
        max_length=255,
        verbose_name='Подзаголовок',
        help_text='Краткое описание содержания страницы',
    )

    body = StreamField(
        [
            ('heading', CharBlock(
                label='Заголовок параграфа', max_length=255,
                help_text="Заголовки отобразятся в панели навигации по странице")),
            ('text', RichTextBlock(
                features=['bold', 'italic', 'h5', 'h6', 'hr', 'link', 'document-link'],
                label='Текст', collapsed=True)),
            ('alert', RichTextBlock(
                features=['bold', 'italic', 'h5', 'h6', 'hr', 'link', 'document-link'],
                label='Выделенный текст', icon='info-circle', collapsed=True)),
            ('subscription', CharBlock(
                label='Подпись под материалом', template='blocks/subscription_block.html',
                collapsed=True, icon='italic')),
            ('image', ImageChooserBlock(label='Изображение', template='blocks/image_description_block.html')),
            ('table', TableBlock(label='Таблица', template='blocks/opened_sections_block.html')),
            ('list', ListBlock(RichTextBlock(
                label="Элемент списка",
                features=['bold', 'italic', 'hr', 'ul', 'link']
            ), label='Перечисление', icon='list-ol', template='blocks/list_block.html', collapsed=True)),
            ('flush', ListBlock(RichTextBlock(
                label="Элемент списка",
                features=['bold', 'italic', 'hr', 'ul', 'link']
            ), label='Список', icon='list-ul', template='blocks/flush_block.html', collapsed=True)),
            ('embed', EmbedBlock(label='Ссылка на медиаматериал', icon='media', collapsed=True)),
            ('html', RawHTMLBlock(label='Сторонний виджет', icon='link-external', collapsed=True)),
        ],
        blank=True,
        verbose_name='Контент',
    )

    staff_only = models.BooleanField(
        default=False,
        verbose_name='Только для сотрудников',
        help_text='Показывать только для сотрудников',
    )

    class Meta:
        verbose_name = 'Страница с инструкцией'
        verbose_name_plural = 'Страницы с инструкциями'

    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
        FieldPanel('body'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('staff_only'),
    ]


class ControlsPage(Page):

    subpage_types = []
    parent_page_types = ['cms.HomePage']
    max_count = 1

    allow_no_source = models.BooleanField(
        default=True,
        verbose_name='Обязателен ли список литературы?',
        help_text='Позволить загружать тезисы / текст докладов, не указав ни одного источника',
    )

    overwrite_academic_title = models.BooleanField(
        default=False,
        verbose_name='Указывать ли «ученое звание отсутствует», если оно не указано автором?',
        help_text='Указывать в информации о научном руководителе — «ученое звание отсутствует» в тезисах / статьях, '
                  'если оно не указано автором'
    )

    confirm_participation = models.BooleanField(
        default=False,
        verbose_name='Попросить авторов дополнительно подтвердить участие в конференции',
        help_text='Попросить авторов дополнительно подтвердить участие в конференции',
    )

    title_length = models.IntegerField(
        default=500,
        verbose_name='Максимальная длина заголовка',
        help_text='Измеряется количеством символов включая пробелы',
    )

    abstract_length = models.IntegerField(
        default=1000,
        verbose_name='Максимальная длина аннотации',
        help_text='Измеряется количеством символов включая пробелы',
    )

    keyword_length = models.IntegerField(
        default=9,
        verbose_name='Максимальное количество ключевых слов',
        help_text='Ключевые слова отделяются между собой запятыми',
    )

    registration_close_date = models.DateTimeField(
        default=datetime(2024, 12, 31, 23, 59, 59),
        verbose_name='Дата закрытия регистрации',
        help_text='Дата закрытия регистрации',
    )

    max_search_results = models.IntegerField(
        default=30,
        verbose_name='Максимальное количество выдаваемых результатов на странице «Все материалы»',
        help_text='Максимальное количество выдаваемых результатов на странице «Все материалы»',
    )

    is_editing_on = models.BooleanField(
        default=True,
        verbose_name='Включить автоматическую вёрстку загружаемых материалов',
        help_text='Включает / отключает автоматизированную вёрстку загружаемых тезисов и текстов докладов. \
        При отключении на облачное хранилище материалы будут загружаться в таком виде, в каком их отправили авторы.',
    )

    imprint = StreamField([
        ('imprint', CollectionImprintBlock(
                                label='Выходные сведения',
                                icon='user', max_count=1))
    ], blank=True,
        verbose_name='Выходные сведения',
        help_text='Используется при составлении титульного листа сборника трудов',)

    editors = StreamField([
        ('editors_list', ListBlock(EditorBlock(label="Редактор", collapsed=True)))
    ], blank=True, null=True, verbose_name="Ред. коллегия",
        help_text="Сотрудники, которые будут указаны на титульном листе сборника трудов конференции", collapsed=True)

    class Meta:
        verbose_name = 'Панель управления'
        verbose_name_plural = 'Панели управления'

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('confirm_participation'),
            FieldPanel('title_length'),
            FieldPanel('abstract_length'),
            FieldPanel('keyword_length'),
            FieldPanel('registration_close_date'),
            FieldPanel('max_search_results'),
        ], heading="Ограничения для докладов", help_text="Параметры проверяются при попытке регистрации новых докладов"),
        MultiFieldPanel([
            FieldPanel('imprint'),
            FieldPanel('editors'),
        ], heading="Выходные сведения", help_text="Используется при составлении титульного листа сборника трудов"),
        MultiFieldPanel([
            InlinePanel('section_moderator', label='модератор'),
        ], heading="Модераторы секций", help_text="Используется при составлении научной программы конференции")
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('max_search_results'),
        FieldPanel('overwrite_academic_title'),
        FieldPanel('allow_no_source'),
        FieldPanel('is_editing_on'),
    ]


class SectionModerator(models.Model):
    controls_panel = ParentalKey(ControlsPage, on_delete=models.CASCADE, null=True, related_name="section_moderator")

    name = models.CharField(max_length=255, blank=True, null=True, verbose_name='ФИО')
    section = models.CharField(max_length=255, blank=True, null=True, verbose_name='Секция')
    degree = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ученая степень')
    academic_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Учёное звание')
    job = models.CharField(max_length=255, blank=True, null=True, verbose_name='Место работы')
    job_title = models.CharField(max_length=255, blank=True, null=True, verbose_name='Должность')


class BaseMailPage(Page):

    subpage_types = ['cms.MailPage']
    parent_page_types = ['cms.HomePage']
    max_count = 1

    site = models.ForeignKey('wagtailcore.Site', on_delete=models.SET_NULL, verbose_name='Сайт', related_name='mail_title', null=True)

    subject_suffix = models.TextField(
        null=True,
        blank=True,
        verbose_name='Окончание тем писем',
        help_text='Будет добавлено в конце темы письма. \
        Например: "Подтверждение адреса электронной почты - {{ Содержимое этого поля }}". \
        Если поле пустое, то по-умолчанию добавляется название текущего сайта.',
    )

    base_footer = models.TextField(
        null=True,
        blank=True,
        verbose_name='Подвал письма',
        help_text='Используется по умолчанию для всех писем, в которых не указан собственный подвал',
    )

    class Meta:
        verbose_name = 'Управление почтовыми рассылками'
        verbose_name_plural = 'Управление почтовыми рассылками'

    content_panels = Page.content_panels + [
        FieldPanel('subject_suffix'),
        FieldPanel('base_footer'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('site'),
    ]


class MailPage(Page):

    subpage_types = []
    parent_page_types = ['cms.BaseMailPage']

    subject = models.CharField(max_length=255, blank=True, null=True, verbose_name='Тема письма')

    header = models.TextField(
        null=True,
        blank=True,
        verbose_name='Заголовок письма',
        help_text='Если не указан, то будет использован заголовок по умолчанию',
    )

    content = StreamField([
        ("mail_text", RichTextBlock(
                features=['bold', 'italic', 'h6', 'hr', 'link', 'ol', 'ul'],
                label='Текст', collapsed=True)),
        ('mail_table', TableBlock(label='Таблица', template='blocks/opened_sections_block.html'))
    ], blank=True,
        verbose_name='Текст письма',
        help_text='Текст письма')

    footer = models.TextField(
        null=True,
        blank=True,
        verbose_name='Подвал письма',
        help_text='Если не указан, то будет использован подвал по умолчанию',
    )

    attachments = StreamField([
        ("mail_attachment", DocumentChooserBlock(label='Прикрепить файл к письму', required=False)),
    ], blank=True,
        verbose_name='Прикрепленные файлы',
        help_text='Файлы, которые будут отправлены вместе с письмом')

    template_code = models.IntegerField(
        choices=mail_template_choices,
        default=MailTemplateCode.Default,
        verbose_name='Тип писем',
        help_text='Письма, к которым будет применяться этот шаблон',
    )

    class Meta:
        verbose_name = 'Шаблон письма'
        verbose_name_plural = 'Шаблоны писем'
        indexes = [
            models.Index(fields=['template_code']),
        ]

    content_panels = Page.content_panels + [
        FieldPanel('subject'),
        FieldPanel('header'),
        FieldPanel('content'),
        FieldPanel('footer'),
        FieldPanel('attachments'),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel('template_code'),
    ]

from django.db import models
from wagtail.admin.panels import FieldPanel
from wagtail.blocks import RichTextBlock

from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from .blocks import FooterBlock


@register_snippet
class Footer(models.Model):

    body = StreamField(
        [
            ('template', FooterBlock(label='Заполнить шаблон')),
            ('text', RichTextBlock(label='Текст')),
        ],
        blank=True,
        verbose_name='Контент',
    )

    panels = [
        FieldPanel('body'),
    ]

    class Meta:
        verbose_name = 'Футер'
        verbose_name_plural = 'Футеры'

    def __str__(self):
        return "Футер"

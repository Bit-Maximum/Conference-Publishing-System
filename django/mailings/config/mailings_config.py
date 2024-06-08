import enum


class MailTemplateCode(enum.IntEnum):
    Default = 0
    AddArticle = 1
    EmailVerification = 2


class RecipientsType(enum.IntEnum):
    All = 0
    NoArticle = 1
    EmailVerification = 2


# mail_template_choices = (
#     ('Отправка по расписанию', (
#         (MailTemplateCode.AddArticle, 'Напоминание зарегистрировать доклад')
#     )),
#     ('Автоматические письма', (
#         (MailTemplateCode.EmailVerification, 'Подтверждение электронной почты'),
#     )),
# )

mail_template_choices = (
    (MailTemplateCode.Default, 'Не выбрано'),
    (MailTemplateCode.AddArticle, 'Напоминание зарегистрировать доклад'),
    (MailTemplateCode.EmailVerification, 'Подтверждение электронной почты'),
)

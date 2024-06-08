from celery import shared_task

import random
import time

from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, EMAIL_PAGE_DOMAIN
from conference.models import CustomUser, ArticleInfo
from django.template.loader import render_to_string

from mailings.config.mailings_config import MailTemplateCode, mail_template_choices, RecipientsType
from cms.views import get_mail_context


@shared_task
def add_article_mail_task(deadline):
    print("Collect data")
    if not deadline:
        print("No deadline provided. Operation canceled")
        return

    recipients = get_recipients(RecipientsType.NoArticle)
    print(recipients)
    print(recipients[0][0])
    if not recipients:
        print("No recipients found. Operation canceled")
        return

    print("Email will be sent to " + str(len(recipients)) + " residents.")
    profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
    subject, footer, site = get_mail_context("Регистрация доклада")

    for i, current in enumerate(recipients):
        if i % 5 == 0:
            print(f"Sending: {i}/{len(recipients)}")

        send_mail(
            subject=subject,
            message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}». Просим вас в срок до {deadline} зарегистрировать свой доклад на сайте конференции, если вы этого ещё не сделали. Авторы, не зарегистрировавшие свой доклад до назначенного времени, не будут допущены к участию в конференции.\nЗарегистрировать доклад можно в вашем личном кабинете.\n\n{footer}",
            html_message=render_to_string('conference/emails/mailings/reminders/add_article.html',
                                          {"profile_url": profile_url, "deadline": deadline,
                                           "last_name": current[1], "first_name": current[2],
                                           "middle_name": current[3], "site": site, "footer": footer}),
            from_email=EMAIL_HOST_USER,
            recipient_list=[current[0]]
        )
        time.sleep(60 + int(random.random() * 15))
    print("Reminders sent")


def get_recipients(recipients_type):
    if recipients_type == RecipientsType.NoArticle:
        recipients = CustomUser.objects.filter(
            articleinfo__isnull=True,
            is_staff=False
        ).values_list('email', 'last_name', 'first_name', 'middle_name')
        return recipients


@shared_task
def mailings_task_test():
    print("\nMailings task test\n")
    return


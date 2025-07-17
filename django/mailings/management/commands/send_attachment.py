import os
import random
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import MASS_FROM_EMAIL, MASS_EMAIL_HOST_USER, MASS_EMAIL_HOST_PASSWORD, EMAIL_PAGE_DOMAIN, STATIC_ROOT, DEFAULT_FROM_EMAIL
from conference.models import CustomUser, ArticleInfo
from django.template.loader import render_to_string
from mailings.views import send_mail_attachments
from cms.views import get_mail_context


class Command(BaseCommand):
    help = 'Send emails with program to users how register their article and it`s not rejected'

    def handle(self, *args, **options):
        print("Collect data")
        recipients = get_recipients()
        recipients = recipients[61:]
        print(recipients[0:3])
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile')
        subject, footer, site = get_mail_context('Программа конференции')
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        i = 0
        for current in recipients:
            print(f"{current[0]} : {current[1]} {current[2]}")
            if i % 5 == 0:
                print(f"Sending: {i}/{len(recipients)}")

            send_mail_attachments(
                subject=subject,
                message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nИнформируем Вас, о том, что Ваш доклад включен в программу научной конференции «{site}». Отправляем Вам регламент работы конференции. Полная программа конференции будет отправлена дополнительно.\nПросим всех докладчиков подтвердить свое участие в вашем личном кабинете на сайте конференции.\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/send_program.html',
                                              {"profile_url": profile_url, "last_name": current[1],
                                               "first_name": current[2], "middle_name": current[3],
                                               "response_email": DEFAULT_FROM_EMAIL, "site": site, "footer": footer}),
                from_email=MASS_FROM_EMAIL,
                auth_user=MASS_EMAIL_HOST_USER,
                auth_password=MASS_EMAIL_HOST_PASSWORD,
                recipient_list=[current[0]],
                attachments_list=[os.path.join(STATIC_ROOT, "conference", "docs", "Программа конференции.pdf")]
            )
            time.sleep(60 + int(random.random() * 15))
            i += 1
        print("program sent")


def get_recipients():
    recipients = CustomUser.objects.filter(
        is_staff=False,
        articleinfo__isnull=False,
        articleinfo__rejected__isnull=True
    ).values_list('email', 'last_name', 'first_name', 'middle_name').distinct()
    return recipients

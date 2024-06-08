import random
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, EMAIL_PAGE_DOMAIN
from conference.models import CustomUser, ArticleInfo
from django.template.loader import render_to_string
from cms.views import get_mail_context


class Command(BaseCommand):
    help = 'Send email to users how don`t add thesis to their article'

    def add_arguments(self, parser):
        # Здесь вы можете добавить свои собственные аргументы
        parser.add_argument('deadline', type=str, help='deadline to make changes')

    def handle(self, *args, **options):
        print("Collect data")
        if not options.get('deadline'):
            print("No deadline provided. Operation canceled")
            return

        deadline = options.get('deadline')
        recipients = get_recipients()
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        subject, footer, site = get_mail_context("Добавление тезисов")
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        for i in range(0, len(recipients), 5):
            print(f"Sending: {i}/{len(recipients)}")
            current_residents = recipients[i:i + 5]
            send_mail(
                subject=subject,
                message=f"Здравствуйте!\n\nРанее вы прошли регистрацию на научную конференцию «{site}». Просим вас в срок до { deadline } загрузить тезисы вашего доклада на сайт конференции, если вы этого ещё не сделали.\nЗагрузить тезисы можно на странице вашего доклада. Попасть на неё вы можете через свой личный кабинет.\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/spam/add_thesis.html',
                                              {"profile_url": profile_url, "deadline": deadline,
                                               "site": site, "footer": footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=current_residents
            )
            time.sleep(200 + int(random.random() * 30))
        print("Reminders sent")


def get_recipients():
    articles = ArticleInfo.objects.filter(related_thesis__isnull=True).values('id')

    recipients = CustomUser.objects.filter(
        articleinfo__in=articles
    ).values_list('email', flat=True)
    return recipients


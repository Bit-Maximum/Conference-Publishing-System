import random
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import MASS_FROM_EMAIL, MASS_EMAIL_HOST_USER, MASS_EMAIL_HOST_PASSWORD, EMAIL_PAGE_DOMAIN
from conference.models import CustomUser, ArticleInfo
from django.template.loader import render_to_string
from mailings.views import send_mail_attachments
from cms.views import get_mail_context


class Command(BaseCommand):
    help = 'Send emails reminders to users how`s article has won'

    def add_arguments(self, parser):
        parser.add_argument('deadline', type=str, help='deadline to make changes')

    def handle(self, *args, **options):
        print("Collect data")
        recipients = get_recipients()
        print(recipients[0:3])
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        deadline = options.get('deadline')
        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        instruction_url = EMAIL_PAGE_DOMAIN + reverse('article_instruction').strip('/')
        subject, footer, site = get_mail_context('Публикация доклада ')
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        i = 0
        for current in recipients:
            if i % 5 == 0:
                print(f"Sending: {i}/{len(recipients)}")

            send_mail_attachments(
                subject=subject,
                message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВаш доклад «{ current[4] }» был рекомендован для включения в сборник трудов конференции «{site}». Просим вас в срок до { deadline } загрузить полный текст вашего доклада на сайт конференции, если вы этого ещё не сделали.\nЗагрузить полный текст можно на странице вашего доклада. Попасть на неё вы можете через свой личный кабинет.\nОбратите внимание, что загружаемы вами документ должен быть оформлен в соответствии с требованиями к тексту докладов\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/reminders/add_article_text.html',
                                              {"profile_url": profile_url, "instruction_url": instruction_url,
                                               "last_name": current[1], "first_name": current[2],
                                               "middle_name": current[3], "title": current[4], "deadline": deadline,
                                               "site": site, "footer": footer}),
                from_email=MASS_FROM_EMAIL,
                auth_user=MASS_EMAIL_HOST_USER,
                auth_password=MASS_EMAIL_HOST_PASSWORD,
                recipient_list=[current[0]],
                attachments_list=None
            )
            time.sleep(60 + int(random.random() * 15))
            i += 1
        print("reminders sent")


def get_recipients():
    recipients = CustomUser.objects.filter(
        is_staff=False,
        articleinfo__isnull=False,
        articleinfo__is_winner=True,
        articleinfo__rejected__isnull=True
    ).values_list('email', 'last_name', 'first_name', 'middle_name', "articleinfo__title").distinct()
    return recipients

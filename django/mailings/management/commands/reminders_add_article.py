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
    help = 'Send email to users how don`t add any article'

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
        print(recipients[0:3])
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        subject, footer, site = get_mail_context('Регистрация доклада')
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        i = 0
        for current in recipients:
            if i % 5 == 0:
                print(f"Sending: {i}/{len(recipients)}")

            send_mail(
                subject=subject,
                message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}». Просим вас в срок до { deadline } зарегистрировать свой доклад на сайте конференции, если вы этого ещё не сделали. Авторы, не зарегистрировавшие свой доклад до назначенного времени, не будут допущены к участию в конференции.\nЗарегистрировать доклад можно в вашем личном кабинете.\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/reminders/add_article.html',
                                              {"profile_url": profile_url, "deadline": deadline,
                                               "last_name": current[1], "first_name": current[2],
                                               "middle_name": current[3], "site": site, 'footer': footer}),
                from_email=EMAIL_HOST_USER,
                recipient_list=[current[0]]
            )
            time.sleep(60 + int(random.random() * 15))
            i += 1
        print("Reminders sent")


def get_recipients():
    recipients = CustomUser.objects.filter(
        articleinfo__isnull=True,
        is_staff=False
    ).values_list('email', 'last_name', 'first_name', 'middle_name')
    return recipients


import time
import random

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST
from django.template.loader import render_to_string
from cms.views import get_mail_context
from mailings.views import send_email_error_massage, get_recipients
from mailings.config.mailings_config import RecipientsType


class Command(BaseCommand):
    help = 'Send email to users how don`t add sources to their article'

    def add_arguments(self, parser):
        # Здесь вы можете добавить свои собственные аргументы
        parser.add_argument('deadline', type=str, help='deadline to make changes')

    def handle(self, *args, **options):
        print("Collect data")
        if not options.get('deadline'):
            print("No deadline provided. Operation canceled")
            return

        deadline = options.get('deadline')
        recipients = get_recipients(RecipientsType.NoSources)
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        subject, footer, site = get_mail_context("Добавление научных источников")
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        i = 0
        bans_counter = 0
        while i < len(recipients) and bans_counter < len(MASS_EMAILS_LIST):
            current = recipients[i]
            if i % 5 == 0:
                print(f"Sending: {i}/{len(recipients)}")
            try:
                send_mail(
                    subject=subject,
                    message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}» с докладом «{current[4]}». Просим вас в срок до {deadline} указать используемые при подготовке доклада научные источники на сайте конференции, если вы этого ещё не сделали.\nУказать используемые источники можно на странице вашего доклада (раздел «Используемые источники»). Попасть на неё вы можете через свой личный кабинет.\n\n{footer}",
                    html_message=render_to_string('conference/emails/mailings/reminders/add_sources.html',
                                                  {"profile_url": profile_url, "deadline": deadline,
                                                   "last_name": current[1], "first_name": current[2],
                                                   "middle_name": current[3], "title": current[4], "site": site,
                                                   "footer": footer}),
                    from_email=MASS_EMAILS_LIST[bans_counter][0],
                    auth_user=MASS_EMAILS_LIST[bans_counter][0],
                    auth_password=MASS_EMAILS_LIST[bans_counter][1],
                    recipient_list=[current[0]]
                )
            except Exception as e:
                print(f"{MASS_EMAILS_LIST[bans_counter][0]} - отключён с ошибкой: {e}")
                bans_counter += 1
            time.sleep(60 + int(random.random() * 30))
            i += 1

        if bans_counter < len(MASS_EMAILS_LIST):
            print("Reminders sent")
            return
        send_email_error_massage(i, len(recipients), recipients[i])

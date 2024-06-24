import random
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST
from django.template.loader import render_to_string
from cms.views import get_mail_context
from mailings.views import send_email_error_massage


class Command(BaseCommand):
    help = 'Test command to send emails to residents'

    def add_arguments(self, parser):
        # Здесь вы можете добавить свои собственные аргументы
        parser.add_argument('args', type=str, help='deadline to make changes')

    def handle(self, *args, **options):
        print("Collect data")
        if not args:
            print("No Arguments provided. Operation canceled")
            return

        deadline = options.get('args')
        recipients = ((EMAIL_HOST_USER, 'Фамилия', 'Имя', 'Отчество'),)
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        print("Email will be sent to " + str(len(recipients)) + " residents.")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        subject, footer, site = get_mail_context("Регистрация доклада")

        i = 0
        bans_counter = 0
        while i < len(recipients) and bans_counter < len(MASS_EMAILS_LIST):
            current = recipients[i]
            if i % 5 == 0:
                print(f"Sending: {i}/{len(recipients)}")
            try:
                send_mail(
                    subject=subject,
                    message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}». Просим вас в срок до {args} зарегистрировать свой доклад на сайте конференции, если вы этого ещё не сделали. Авторы, не зарегистрировавшие свой доклад до назначенного времени, не будут допущены к участию в конференции.\nЗарегистрировать доклад можно в вашем личном кабинете.\n\n{footer}",
                    html_message=render_to_string('conference/emails/mailings/reminders/add_article.html',
                                                  {"profile_url": profile_url, "deadline": args,
                                                   "last_name": current[1], "first_name": current[2],
                                                   "middle_name": current[3], "site": site, "footer": footer}),
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


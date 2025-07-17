import random
import time

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST
from django.template.loader import render_to_string
from cms.views import get_mail_context
from mailings.views import send_email_error_massage, get_recipients
from mailings.config.mailings_config import RecipientsType


class Command(BaseCommand):
    help = 'Send emails reminders to users how`s article has won'

    def add_arguments(self, parser):
        parser.add_argument('deadline', type=str, help='deadline to make changes')

    def handle(self, *args, **options):
        print("Collect data")
        if not options.get('deadline'):
            print("No deadline provided. Operation canceled")
            return

        recipients = get_recipients(RecipientsType.Winners)
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        deadline = options.get('deadline')
        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
        instruction_url = EMAIL_PAGE_DOMAIN + reverse('article_instruction').strip('/')
        subject, footer, site = get_mail_context('Публикация доклада')
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
                    message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВаш доклад «{current[4]}» был рекомендован для включения в сборник трудов конференции «{site}». Просим вас в срок до {deadline} загрузить полный текст вашего доклада на сайт конференции, если вы этого ещё не сделали.\nЗагрузить полный текст можно на странице вашего доклада. Попасть на неё вы можете через свой личный кабинет.\nОбратите внимание, что загружаемы вами документ должен быть оформлен в соответствии с требованиями к тексту докладов\n\n{footer}",
                    html_message=render_to_string('conference/emails/mailings/reminders/add_article_text.html',
                                                  {"profile_url": profile_url, "instruction_url": instruction_url,
                                                   "last_name": current[1], "first_name": current[2],
                                                   "middle_name": current[3], "title": current[4], "deadline": deadline,
                                                   "site": site, "footer": footer}),
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

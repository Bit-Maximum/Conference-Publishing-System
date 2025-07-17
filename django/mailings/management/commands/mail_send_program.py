import os
import random
import shutil
import time

from django.core.management.base import BaseCommand
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, YADISK_TOKEN, TEMP_FILE_DIR, YADISK_MAILINGS_SEND_PROGRAM_PATH, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST, DEFAULT_FROM_EMAIL, STATIC_CROSS_PLATFORM
from django.template.loader import render_to_string

from mailings.config.mailings_config import MailTemplateCode, mail_template_choices, RecipientsType
from cms.views import get_mail_context
from mailings.views import send_email_error_massage, download_mail_attachments, get_recipients, send_mail_attachments


class Command(BaseCommand):
    help = 'Send emails with program to users how register their article and it`s not rejected'

    def handle(self, *args, **options):
        print("Collect data")
        recipients = get_recipients(RecipientsType.HasArticle)
        if not recipients:
            print("No recipients found. Operation canceled")
            return

        confirm = input("Email will be sent to " + str(len(recipients)) + " residents. Continue? (y/N): ")
        profile_url = EMAIL_PAGE_DOMAIN + reverse('profile')
        subject, footer, site = get_mail_context('Программа конференции')
        if confirm.lower() != "y":
            print("Operation canceled")
            return

        temp_dir = os.path.join(TEMP_FILE_DIR, 'mailings', 'send_program')
        attachments = download_mail_attachments(temp_dir)
        if not attachments:
            if os.path.exists(os.path.join(STATIC_CROSS_PLATFORM, "conference", "docs", "Программа конференции.pdf")):
                attachments = [os.path.join(STATIC_CROSS_PLATFORM, "conference", "docs", "Программа конференции.pdf")]
            else:
                print("No attachments found. Operation canceled")
                return
        try:
            i = 0
            bans_counter = 0
            while i < len(recipients) and bans_counter < len(MASS_EMAILS_LIST):
                current = recipients[i]
                if i % 5 == 0:
                    print(f"Sending: {i}/{len(recipients)}")
                try:
                    send_mail_attachments(
                        subject=subject,
                        message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nОтправляем Вам регламент работы конференции научной конференции «{site}» (документ прикреплён к письму).\nПросим всех докладчиков подтвердить свое участие в вашем личном кабинете на сайте конференции.\n\n{footer}",
                        html_message=render_to_string('conference/emails/mailings/send_program.html',
                                                      {"profile_url": profile_url, "last_name": current[1],
                                                       "first_name": current[2], "middle_name": current[3],
                                                       "response_email": DEFAULT_FROM_EMAIL, "site": site,
                                                       "footer": footer}),
                        from_email=MASS_EMAILS_LIST[bans_counter][0],
                        auth_user=MASS_EMAILS_LIST[bans_counter][0],
                        auth_password=MASS_EMAILS_LIST[bans_counter][1],
                        recipient_list=[current[0]],
                        attachments_list=attachments
                    )
                except Exception as e:
                    print(f"{MASS_EMAILS_LIST[bans_counter][0]} - отключён с ошибкой: {e}")
                    bans_counter += 1
                time.sleep(90 + int(random.random() * 60))
                i += 1

            if bans_counter < len(MASS_EMAILS_LIST):
                print("Reminders sent")
                shutil.rmtree(temp_dir)
                return

            send_email_error_massage(i, len(recipients), recipients[i])
            shutil.rmtree(temp_dir)
        except Exception as e:
            print(e)
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass

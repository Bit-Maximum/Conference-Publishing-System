import shutil
from tempfile import NamedTemporaryFile

import yadisk
from celery import shared_task

import random
import time
import os

from django.core.mail import send_mail
from django.urls import reverse

from publisher.settings import EMAIL_HOST_USER, YADISK_TOKEN, TEMP_FILE_DIR, YADISK_MAILINGS_SEND_PROGRAM_PATH, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST, DEFAULT_FROM_EMAIL, STATIC_CROSS_PLATFORM
from django.template.loader import render_to_string

from mailings.config.mailings_config import MailTemplateCode, mail_template_choices, RecipientsType
from cms.views import get_mail_context
from mailings.views import send_email_error_massage, download_mail_attachments, get_recipients, send_mail_attachments


@shared_task
def add_article_mail_task(deadline):
    print("Collect data")
    if not deadline:
        print("No deadline provided. Operation canceled")
        return

    recipients = get_recipients(RecipientsType.NoArticle)
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
                message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}». Просим вас в срок до {deadline} зарегистрировать свой доклад на сайте конференции, если вы этого ещё не сделали. Авторы, не зарегистрировавшие свой доклад до назначенного времени, не будут допущены к участию в конференции.\nЗарегистрировать доклад можно в вашем личном кабинете.\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/reminders/add_article.html',
                                              {"profile_url": profile_url, "deadline": deadline,
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


@shared_task
def add_thesis_mail_task(deadline):
    print("Collect data")
    if not deadline:
        print("No deadline provided. Operation canceled")
        return

    recipients = get_recipients(RecipientsType.NoThesis)
    if not recipients:
        print("No recipients found. Operation canceled")
        return

    profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
    subject, footer, site = get_mail_context('Добавление тезисов')

    i = 0
    bans_counter = 0
    while i < len(recipients) and bans_counter < len(MASS_EMAILS_LIST):
        current = recipients[i]
        if i % 5 == 0:
            print(f"Sending: {i}/{len(recipients)}")
        try:
            send_mail(
                subject=subject,
                message=f"Здравствуйте, {current[1]} {current[2]} {current[3]}!\n\nВы подали заявку на участие в научной конференции «{site}» с докладом «{current[4]}». Просим вас в срок до {deadline} загрузить тезисы вашего доклада на сайт конференции, если вы этого ещё не сделали.\nЗагрузить тезисы можно на странице вашего доклада. Попасть на неё вы можете через свой личный кабинет.\nЗагрузить тезисы можно на странице вашего доклада. Попасть на неё вы можете через свой личный кабинет.\n\n{footer}",
                html_message=render_to_string('conference/emails/mailings/reminders/add_thesis.html',
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


@shared_task
def add_sources_mail_task(deadline):
    print("Collect data")
    if not deadline:
        print("No deadline provided. Operation canceled")
        return

    recipients = get_recipients(RecipientsType.NoSources)
    if not recipients:
        print("No recipients found. Operation canceled")
        return

    print("Email will be sent to " + str(len(recipients)) + " residents.")
    profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
    subject, footer, site = get_mail_context("Добавление научных источников")

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


@shared_task
def add_text_mail_task(deadline):
    print("Collect data")
    if not deadline:
        print("No deadline provided. Operation canceled")
        return

    recipients = get_recipients(RecipientsType.Winners)
    if not recipients:
        print("No recipients found. Operation canceled")
        return

    print("Email will be sent to " + str(len(recipients)) + " residents.")
    profile_url = EMAIL_PAGE_DOMAIN + reverse('profile').strip('/')
    instruction_url = EMAIL_PAGE_DOMAIN + reverse('article_instruction').strip('/')
    subject, footer, site = get_mail_context('Публикация доклада')

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


@shared_task
def send_program_mail_task():
    print("Collect data")
    recipients = get_recipients(RecipientsType.HasArticle)
    if not recipients:
        print("No recipients found. Operation canceled")
        return

    print("Email will be sent to " + str(len(recipients)) + " residents")
    profile_url = EMAIL_PAGE_DOMAIN + reverse('profile')
    subject, footer, site = get_mail_context('Программа конференции')

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
            shutil.rmtree(temp_dir)
            print("Reminders sent")
            return

        send_email_error_massage(i, len(recipients), recipients[i])
        shutil.rmtree(temp_dir)
    except Exception as e:
        print(e)
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


@shared_task
def mailings_task_test(args):
    print("Collect data")
    if not args:
        print("No Arguments provided. Operation canceled")
        return

    # args = ''.join(args)
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



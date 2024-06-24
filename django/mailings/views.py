import time
from tempfile import NamedTemporaryFile

import puremagic
import os

import yadisk
from publisher.settings import EMAIL_HOST_USER, YADISK_MAILINGS_SEND_PROGRAM_PATH, EMAIL_PAGE_DOMAIN, MASS_EMAILS_LIST, YADISK_TOKEN
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.template.loader import render_to_string

from mailings.config.mailings_config import RecipientsType
from conference.models import CustomUser, ArticleInfo


def send_mail_attachments(subject, message, html_message, from_email, recipient_list, fail_silently=False,
                          auth_user=None, auth_password=None, connection=None, attachments_list=None):
    """
    Given a datatuple of (subject, text_content, html_content, from_email,
    recipient_list), sends each message to each recipient list. Returns the
    number of emails sent.

    If from_email is None, the DEFAULT_FROM_EMAIL setting is used.
    If auth_user and auth_password are set, they're used to log in.
    If auth_user is None, the EMAIL_HOST_USER setting is used.
    If auth_password is None, the EMAIL_HOST_PASSWORD setting is used.

    """
    connection = connection or get_connection(
        username=auth_user, password=auth_password, fail_silently=fail_silently)
    messages = []
    message = EmailMultiAlternatives(subject, message, from_email, recipient_list)
    message.attach_alternative(html_message, 'text/html')
    if attachments_list:
        for path in attachments_list:
            with open(path, 'rb') as file:
                mime_type = puremagic.from_stream(file, mime=True)
                file_content = file.read()

            file_name = os.path.basename(path)
            message.attach(file_name, file_content, mime_type)
    messages.append(message)
    return connection.send_messages(messages)


def send_email_with_attachment(subject, message, from_email, recipient_list, attachment_path, auth_user, auth_pass):
    with open(attachment_path, 'rb') as file:
        file_content = file.read()

    mime_type = puremagic.from_stream(file_content, mime=True)
    file_name = os.path.basename(attachment_path)

    if len(recipient_list) == 0:
        return

    connection = get_connection(username=auth_user, password=auth_pass)

    email = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
    email.attach(file_name, file_content, mime_type)

    connection.send_message(email)


def send_email_error_massage(error_at_index, total_recipients, last_sent):
    print("All emails are banned")
    print(f"Last error on {error_at_index} / {total_recipients}: {last_sent}")
    print(f"Sending crush report")
    send_mail(
        subject="Ошибка во время отправки почтовых уведомлений",
        message=f"Здравствуйте!!\n\nВо время отправки почтовых уведомлений произошла ошибка.\n\nОшибка случилась во время отправки {error_at_index} (из {total_recipients}): было отправлено {last_sent}.",
        html_message=render_to_string('conference/emails/mailings/error.html',
                                      {"index": error_at_index, "total": total_recipients,
                                       "last_sent": last_sent}),
        from_email=EMAIL_HOST_USER,
        recipient_list=EMAIL_HOST_USER
    )


def get_recipients(recipients_type):
    if recipients_type == RecipientsType.NoArticle:
        recipients = CustomUser.objects.filter(
            articleinfo__isnull=True,
            is_staff=False
        ).values_list('email', 'last_name', 'first_name', 'middle_name').distinct()
        return recipients
    elif recipients_type == RecipientsType.NoThesis:
        recipients = CustomUser.objects.filter(
            is_staff=False,
            articleinfo__isnull=False,
            articleinfo__related_thesis__isnull=True
        ).values_list('email', 'last_name', 'first_name', 'middle_name', 'articleinfo__title').distinct()
        return recipients
    elif recipients_type == RecipientsType.NoSources:
        recipients = CustomUser.objects.filter(
            is_staff=False,
            articleinfo__isnull=False,
            articleinfo__related_thesis__isnull=False,
            articleinfo__related_source__isnull=True,
        ).values_list('email', 'last_name', 'first_name', 'middle_name', 'articleinfo__title').distinct()
        return recipients
    elif recipients_type == RecipientsType.Winners:
        recipients = CustomUser.objects.filter(
            is_staff=False,
            articleinfo__isnull=False,
            articleinfo__is_winner=True,
            articleinfo__rejected__isnull=True
        ).values_list('email', 'last_name', 'first_name', 'middle_name', "articleinfo__title").distinct()
        return recipients
    elif recipients_type == RecipientsType.HasArticle:
        recipients = CustomUser.objects.filter(
            is_staff=False,
            articleinfo__isnull=False,
            articleinfo__rejected__isnull=True
        ).values_list('email', 'last_name', 'first_name', 'middle_name').distinct()
        return recipients


def download_mail_attachments(dir_out, cloud=None):
    if cloud is None:
        cloud = yadisk.YaDisk(token=YADISK_TOKEN)

    uploaded_files = []
    files = list(cloud.listdir(YADISK_MAILINGS_SEND_PROGRAM_PATH))
    try:
        os.makedirs(dir_out)
    except Exception:
        pass

    for file in files:
        with NamedTemporaryFile(suffix=file.name.split('.')[-1]) as temp_file:
            path_to_file = os.path.join(dir_out, file.name)
            cloud.download(f"{YADISK_MAILINGS_SEND_PROGRAM_PATH}/{file.name}", temp_file)
            temp_file.seek(0)
            with open(path_to_file, 'wb') as fout:
                fout.write(temp_file.read())
                uploaded_files.append(path_to_file)
    cloud.close()
    return uploaded_files

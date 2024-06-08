import time
import magic
import os

from publisher.settings import MASS_FROM_EMAIL, MASS_EMAIL_HOST_USER, MASS_EMAIL_HOST_PASSWORD, EMAIL_PAGE_DOMAIN
from django.core.mail import get_connection, EmailMultiAlternatives
from django.core.mail import EmailMessage


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
                file_content = file.read()
            mime_type = magic.from_buffer(file_content, mime=True)
            file_name = os.path.basename(path)
            message.attach(file_name, file_content, mime_type)
    messages.append(message)
    return connection.send_messages(messages)


def send_email_with_attachment(subject, message, from_email, recipient_list, attachment_path, auth_user, auth_pass):
    with open(attachment_path, 'rb') as file:
        file_content = file.read()

    mime_type = magic.from_buffer(file_content, mime=True)
    file_name = os.path.basename(attachment_path)

    if len(recipient_list) == 0:
        return

    connection = get_connection(username=auth_user, password=auth_pass)

    email = EmailMessage(subject, message, from_email, recipient_list, connection=connection)
    email.attach(file_name, file_content, mime_type)

    connection.send_message(email)

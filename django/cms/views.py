from cms.models import BaseMailPage


def get_mail_context(base_subject: str):
    mail_db = BaseMailPage.objects.first()
    site = str(mail_db.site.site_name)
    subject_suffix = mail_db.subject_suffix
    footer = mail_db.base_footer

    if not subject_suffix or subject_suffix == '':
        subject_suffix = f"«{site}»"
    if not footer or footer == '':
        footer = f"С уважением, оргкомитет «{site}»."

    subject = f"{base_subject} - {subject_suffix}"
    return subject, footer, site

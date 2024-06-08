from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY')

DEBUG = os.environ.get('DEBUG')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS').split(',')


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


STATIC_DIR = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [STATIC_DIR]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # для отладки почтового клиента

EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_HOST_PORT = os.environ.get('EMAIL_HOST_PORT')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')


MASS_FROM_EMAIL = os.environ.get('MASS_FROM_EMAIL')
MASS_EMAIL_HOST_USER = os.environ.get('MASS_EMAIL_HOST_USER')
MASS_EMAIL_HOST_PASSWORD = os.environ.get('MASS_EMAIL_HOST_PASSWORD')


# MASS_FROM_EMAIL = 'humaniora-forum-noreply@yandex.ru' # Резервный
# MASS_EMAIL_HOST_USER = 'humaniora-forum-noreply@yandex.ru' # Резервный
# MASS_EMAIL_HOST_PASSWORD = 'pxuhyazglhvzgeun' # Резервный


# Django-email-verification
EMAIL_FROM_ADDRESS = DEFAULT_FROM_EMAIL
EMAIL_PAGE_DOMAIN = os.environ.get('EMAIL_PAGE_DOMAIN')
EMAIL_MULTI_USER = False  # Allow multiple users with same email. Will user the first one.


def email_verified_callback(user):
    user.is_verified = True


# mandatory for email sending
EMAIL_MAIL_SUBJECT = os.environ.get('EMAIL_MAIL_SUBJECT')
EMAIL_MAIL_HTML = '../../conference/templates/conference/email_verification/verification_mail_body.html'
EMAIL_MAIL_PLAIN = '../../conference/templates/conference/email_verification/verification_mail_plain.txt'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60  # one hour


# mandatory for builtin view
EMAIL_MAIL_PAGE_TEMPLATE = '../../conference/templates/conference/email_verification/verification_success.html'
EMAIL_MAIL_CALLBACK = email_verified_callback

# YaDisk API
YADISK_BASE_PATH = os.environ.get('YADISK_BASE_PATH')
YADISK_TOKEN = os.environ.get('YADISK_TOKEN')
YADISK_ORIGINALS_THESIS_PATH = f"{YADISK_BASE_PATH}/Оригиналы/Тезисы"
YADISK_ORIGINALS_ARTICLE_PATH = f"{YADISK_BASE_PATH}/Оригиналы/Статьи"
YADISK_THESIS_PATH = f"{YADISK_BASE_PATH}/Тезисы"
YADISK_ARTICLE_PATH = f"{YADISK_BASE_PATH}/Статьи"

CLOUD_BASE_URL = os.environ.get('CLOUD_BASE_URL')

# django-crontab
CRONJOBS = [
    ('0 17 * * * ', 'django.core.management.call_command', ['refresh_cloud'])
]

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_BROKER", "redis://redis:6379/0")

# WAGTAIL SETTINGS
WAGTAIL_SITE_NAME = os.environ.get('WAGTAIL_SITE_NAME')

WAGTAILADMIN_BASE_URL = EMAIL_PAGE_DOMAIN

WAGTAILDOCS_EXTENSIONS = ['csv', 'docx', 'key', 'odt', 'pdf', 'pptx', 'rtf', 'txt', 'xlsx', 'zip']

TAGGIT_CASE_INSENSITIVE = True


from pathlib import Path
import os
import environs

BASE_DIR = Path(__file__).resolve().parent.parent

env = environs.Env()
env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')

DEBUG = env.bool('DEBUG', False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', delimiter=',')

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', delimiter=',')

CLOUD_BASE_URL = env('CLOUD_BASE_URL')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{}'.format(
            env('DB_ENGINE', 'sqlite3')
        ),
        'NAME': env('DB_NAME', 'django'),
        'USER': env('DB_USER', 'max'),
        'PASSWORD': env('DB_PASSWORD', 'password'),
        'HOST': env('DB_HOST', '127.0.0.1'),
        'PORT': env.int('DB_PORT', 5432),
        'CONN_MAX_AGE': 120,
    }
}

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = '/static/'

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = 'media/'

# Compose Documents
TEMP_IMG_DIR = os.path.join(MEDIA_ROOT, "temp", "img")
TEMP_FILE_DIR = os.path.join(MEDIA_ROOT, "temp", "file")

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend' # для отладки почтового клиента

EMAIL_HOST = env('EMAIL_HOST')
EMAIL_HOST_PORT = env.int('EMAIL_HOST_PORT')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')


MASS_FROM_EMAIL = env('MASS_FROM_EMAIL')
MASS_EMAIL_HOST_USER = env('MASS_EMAIL_HOST_USER')
MASS_EMAIL_HOST_PASSWORD = env('MASS_EMAIL_HOST_PASSWORD')

MASS_EMAILS_LIST = (
    (MASS_FROM_EMAIL, MASS_EMAIL_HOST_PASSWORD),
)

# Django-email-verification
EMAIL_FROM_ADDRESS = DEFAULT_FROM_EMAIL
EMAIL_PAGE_DOMAIN = env('EMAIL_PAGE_DOMAIN')
EMAIL_MULTI_USER = False  # Allow multiple users with same email. Will send to user the first one.


def email_verified_callback(user):
    user.is_verified = True


# mandatory for email sending
WAGTAIL_SITE_NAME = env('SITE_NAME')
WAGTAILADMIN_BASE_URL = EMAIL_PAGE_DOMAIN
WAGTAILDOCS_EXTENSIONS = ['csv', 'docx', 'key', 'odt', 'pdf', 'pptx', 'rtf', 'txt', 'xlsx', 'zip']
TAGGIT_CASE_INSENSITIVE = True

# mandatory for email sending
EMAIL_MAIL_SUBJECT = f'Подтверждение адреса электронной почты - {WAGTAIL_SITE_NAME}'
EMAIL_MAIL_HTML = '../../conference/templates/conference/email_verification/verification_mail_body.html'
EMAIL_MAIL_PLAIN = '../../conference/templates/conference/email_verification/verification_mail_plain.txt'
EMAIL_MAIL_TOKEN_LIFE = 60 * 60  # one hour

# mandatory for builtin view
EMAIL_MAIL_PAGE_TEMPLATE = '../../conference/templates/conference/email_verification/verification_success.html'
EMAIL_MAIL_CALLBACK = email_verified_callback


# Logging
ADMINS = [
    ('Admin', env('LOGGING_TO_EMAIL')),
]
MANAGERS = ADMINS


# YaDisk API
YADISK_BASE_PATH = env('SITE_NAME')
YADISK_ORIGINALS_DIR = "Оригиналы"
YADISK_TOKEN = env('YADISK_TOKEN')
YADISK_ORIGINALS_THESIS_PATH = f"{YADISK_BASE_PATH}/{YADISK_ORIGINALS_DIR}/Тезисы"
YADISK_ORIGINALS_ARTICLE_PATH = f"{YADISK_BASE_PATH}/{YADISK_ORIGINALS_DIR}/Статьи"
YADISK_THESIS_PATH = f"{YADISK_BASE_PATH}/Тезисы"
YADISK_ARTICLE_PATH = f"{YADISK_BASE_PATH}/Статьи"
YADISK_THESIS_EDITED_PATH = f"{YADISK_BASE_PATH}/Отредактированные тезисы "
YADISK_ARTICLE_EDITED_PATH = f"{YADISK_BASE_PATH}/Отредактированные статьи"

YADISK_MAILINGS_BASE_PATH = f"{YADISK_BASE_PATH}/{YADISK_ORIGINALS_DIR}/Почтовые вложения"
YADISK_MAILINGS_SEND_PROGRAM_PATH = f"{YADISK_MAILINGS_BASE_PATH}/Рассылка программы конференции"

# django-crontab
CRONJOBS = [
    ('0 17 * * * ', 'django.core.management.call_command', ['refresh_cloud'])
]

CELERY_BROKER_URL = env("CELERY_BROKER", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = env("CELERY_BROKER", "redis://redis:6379/0")
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

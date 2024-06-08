from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
USE_DOCKER = False

ROOT_URLCONF = 'publisher.urls'

WSGI_APPLICATION = 'publisher.wsgi.application'

AUTH_USER_MODEL = "conference.CustomUser"

LOGIN_URL = 'login'

INSTALLED_APPS = [
    # This app
    'conference.apps.ConferenceConfig',
    'filemanager.apps.FilemanagerConfig',
    'mailings.apps.MailingsConfig',
    'cms.apps.CmsConfig',

    # Wagtail staff
    'wagtail.contrib.styleguide',
    'wagtail.contrib.table_block',
    'wagtail.contrib.forms',
    'wagtail.contrib.redirects',
    'wagtail.embeds',
    'wagtail.sites',
    'wagtail.users',
    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    # Wagtail Third-Party Apps
    'taggit',
    'modelcluster',

    # Django staff
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Interactive forms staff
    'widget_tweaks',
    'crispy_forms',
    'crispy_bootstrap5',

    # Custom libraries
    'django_celery_beat',
    'wagtail_celery_beat',
    'django_email_verification',
    'django_crontab',
    'corsheaders'
]

MIDDLEWARE = [
    # Django staff
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Wagtail staff
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Asia/Vladivostok'

USE_I18N = True

USE_TZ = True

CORS_ORIGIN_ALLOW_ALL = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
MEDIA_URL = 'media/'

# Compose Documents
TEMP_IMG_DIR = os.path.join(MEDIA_ROOT, "temp", "img")
TEMP_FILE_DIR = os.path.join(MEDIA_ROOT, "temp", "file")

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"

CRISPY_TEMPLATE_PACK = "bootstrap5"

# Wagtail Search
# https://docs.wagtail.org/en/stable/topics/search/backends.html
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

WAGTAIL_ENABLE_UPDATE_CHECK = False

CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

WCB_MENU_HOOK_NAME = 'Периодические задачи'

if USE_DOCKER:
    try:
        from .settings_docker_local import *
    except ImportError:
        from .settings_local import *
else:
    try:
        from .settings_local import *
    except ImportError:
        from .settings_prod import *

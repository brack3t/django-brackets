import contextlib

from django.conf.global_settings import *  # noqa: F401, F403
from django.contrib.messages import constants as message_constants

# Settings deleted to prevent RemovedInDjango 5.0 warnings
REMOVED_SETTINGS = [
    "CSRF_COOKIE_MASKED",
    "DEFAULT_FILE_STORAGE",
    "DEFAULT_HASHING_ALGORITHM",
    "FORMS_URLFIELD_ASSUME_HTTPS",
    "PASSWORD_RESET_TIMEOUT_DAYS",
    "STATICFILES_STORAGE",
    "USE_DEPRECATED_PYTZ",
    "USE_L10N",
]
for setting in REMOVED_SETTINGS:
    with contextlib.suppress(KeyError):
        del globals()[setting]

DEBUG = False
TEMPLATE_DEBUG = DEBUG

TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-US"
SITE_ID = 1
USE_TZ = True

SECRET_KEY = "local"

ROOT_URLCONF = "tests.project.urls"

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "tests.project",
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = []
AUTH_USER_MODEL = "auth.User"
MESSAGE_STORAGE = "django.contrib.messages.storage.cookie.CookieStorage"
MESSAGE_LEVEL = message_constants.DEBUG

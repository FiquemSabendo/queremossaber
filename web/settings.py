"""
Django settings for web project.

Generated by 'django-admin startproject' using Django 2.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ
from django.utils.translation import gettext_lazy as _
from pathlib import Path


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
# Preciso converter pra str por causa de um erro no livesync. Talvez novas
# versões aceitem Path.
BASE_DIR = str(Path(__file__).resolve().parent.parent)

DEFAULT_ENV_PATH = os.path.join(BASE_DIR, ".env")
env = environ.Env(
    DEBUG=(bool, False),
    ENV_PATH=(str, DEFAULT_ENV_PATH),
    ENABLE_S3=(bool, False),
    HEROKU_APP_ID=(str, None),
    SESSION_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_SECURE=(bool, False),
    CSRF_COOKIE_DOMAIN=(str, None),
    CSRF_TRUSTED_ORIGINS=(list, ["queremossaber.org.br"]),
    ENV=(str, "dev"),
)
env.read_env(env.str("ENV_PATH"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")

ENV = env("ENV", default="dev")

ALLOWED_HOSTS = (
    [
        "queremossaber.org.br",
    ]
    + ["localhost", "127.0.0.1"]
    if DEBUG
    else []
)

INTERNAL_IPS = [
    "127.0.0.1",
]

SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
CSRF_COOKIE_DOMAIN = env("CSRF_COOKIE_DOMAIN")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Application definition

extra_apps = []
if ENV == "dev":
    extra_apps += ["livesync"]

INSTALLED_APPS = [
    "web.foi_requests",
    "web.whoami",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "raven.contrib.django.raven_compat",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "debug_toolbar",
] + extra_apps

extra_middleware = []
if ENV == "dev":
    extra_middleware += [
        "livesync.core.middleware.DjangoLiveSyncMiddleware",
    ]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "livesync.core.middleware.DjangoLiveSyncMiddleware",
] + extra_middleware

ROOT_URLCONF = "web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "web", "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "web.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

MAX_CONN_AGE = 600

DATABASES = {
    "default": env.db(),
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "pt-br"

LANGUAGES = [
    ("pt-br", _("Brazilian Portuguese")),
]

LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]

TIME_ZONE = "Brazil/East"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "web", "static"),
]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Uploaded files variables. Will only be used if ENABLE_S3 is False.
MEDIA_URL = "/upload/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")


ENABLE_S3 = env("ENABLE_S3")
if ENABLE_S3:
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_DEFAULT_ACL = "public-read"
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME")
    AWS_S3_ENDPOINT_URL = env("AWS_S3_ENDPOINT_URL")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_LOCATION = env("AWS_LOCATION")
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "public, max-age=31556926",
    }

# FIXME: This is a workaround because WhiteNoise's files storage raises error 500.
# http://whitenoise.evans.io/en/stable/django.html#troubleshooting-the-whitenoise-storage-backend
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

DJANGO_LIVESYNC = {
    "HOST": "localhost",
    "PORT": 9001,
}

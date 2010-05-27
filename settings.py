# -*- coding: UTF-8 -*-
# Django settings for webPyVirt project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    (u"Martin Jantošovič", "jantosovic.martin@gmail.com"),
)

MANAGERS = ADMINS

DATABASE_ENGINE =   "mysql"                 # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME =     "webPyVirt_django"      # Or path to database file if using sqlite3.
DATABASE_USER =     "webPyVirt"             # Not used with sqlite3.
DATABASE_PASSWORD = ""                      # Not used with sqlite3.
DATABASE_HOST =     ""                      # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT =     ""                      # Set to empty string for default. Not used with sqlite3.
DATABASE_OPTIONS = {
    "init_command": "SET storage_engine=INNODB",
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "Europe/Bratislava"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "sk"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = "/home/mordred/projects/webPyVirt/static/"

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "http://webPyVirt.devel/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'j7c1@gx5$w50%vm41v++ya89y2pb)__gc2_nem9!5vu0d%08vn'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    "webPyVirt.middleware.DebugSQLMiddleware",
    'django.middleware.transaction.TransactionMiddleware',
)

ROOT_URLCONF = 'webPyVirt.urls'

TEMPLATE_DIRS = (
    "/home/mordred/projects/webPyVirt/templates/",
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "webPyVirt.context_processors.menu",
)

_ = lambda s: s

LANGUAGES = (
    ("sk", _("Slovak")),
    ("en", _("English")),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    "django_extensions",
    "webPyVirt.accounts",
    "webPyVirt.domains",
    "webPyVirt.monitor",
    "webPyVirt.nodes",
    "webPyVirt.conf"
)

INTERNAL_IPS = ("127.0.0.1", "127.0.1.1", )

DEFAULT_CHARSET = "utf-8"

MONITOR_PID = "/tmp/webPyVirt-monitor.pid"

LOG_FILENAME = "/tmp/webPyVirt-server.log"

if DEBUG:
    import logging
    logging.basicConfig(
        level       = logging.DEBUG,
        format      = "%(asctime)s [ %(levelname)s ]: %(message)s",
        filename    = LOG_FILENAME,
        filemode    = "a"
    )
#endif

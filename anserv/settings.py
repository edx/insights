# Django settings for anserv project.

import os
import sys
from path import path
import datetime

IMPORT_MITX_MODULES = True
MITX_PATH = os.path.abspath("../../mitx/")
DJANGOAPPS_PATH = "{0}/{1}/{2}".format(MITX_PATH, "lms", "djangoapps")
LMS_LIB_PATH = "{0}/{1}/{2}".format(MITX_PATH, "lms", "lib")
COMMON_PATH = "{0}/{1}/{2}".format(MITX_PATH, "common", "djangoapps")

sys.path.append(MITX_PATH)
sys.path.append(DJANGOAPPS_PATH)
sys.path.append(LMS_LIB_PATH)
sys.path.append(COMMON_PATH)

TIME_BETWEEN_DATA_REGENERATION = datetime.timedelta(minutes=1)

#Initialize celery
import djcelery
djcelery.setup_loader()

BASE_DIR = os.path.abspath(os.path.join(__file__, "..", "..", ".."))

ROOT_PATH = path(__file__).dirname()
REPO_PATH = ROOT_PATH.dirname()
ENV_ROOT = REPO_PATH.dirname()

IMPORT_GIT_MODULES = False
GIT_CLONE_URL = "git@github.com:MITx/{0}.git"
COURSE_FILE_PATH = os.path.abspath(os.path.join(ENV_ROOT, "data"))
COURSE_CONFIG_PATH = os.path.abspath(os.path.join(REPO_PATH, "course_listings.json"))

DUMMY_MODE = False

MAKO_TEMPLATES = {'main': 'templates'}
MAKO_MODULE_DIR = 'compiled_templates'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SNS_SUBSCRIPTIONS = []

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

LOGIN_REDIRECT_URL = "/"

DATABASES = {
    'default': { ## Main analytics read replica
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '../../db/mitx.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }, 
    'local': { ## Small, local read/write DB for things like settings, cron tasks, etc. 
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '../../localdb.sql',            # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

DATABASE_ROUTERS = ['an_evt.router.DatabaseRouter']

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache'
    }
}

LOG_READ_DIRECTORY = "../../analytics-logs/"
LOG_POST_URL = "http://127.0.0.1:9022/event"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''


MODULE_RESOURCE_STATIC = os.path.join(ENV_ROOT,'resource')

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'staticfiles.finders.FileSystemFinder',
    'staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'z=*gblf=jnrk9wf7+_ug*of(ayf^$u5myjr^tt$fjlr43wyd3^'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'mitxmako.middleware.MakoMiddleware',
)

ROOT_URLCONF = 'anserv.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    BASE_DIR,
    str(os.path.abspath(REPO_PATH / 'templates/')),
    str(os.path.abspath(REPO_PATH / 'anserv/templates/')),
)

INSTALLED_APPS = (
    'django.contrib.auth',
# contenttypes has weird conflicts with multiple databases. My guess this 
# has something to do with having auth in a read-only DB. 
    'django.contrib.contenttypes', 
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'an_evt',
    'dashboard',
    'modules',
    'modules.page_count',
    'modules.user_stats',
    'mitxmako',
    'djcelery',
    'south',
    'frontend',
    'pipeline',
    'staticfiles',
    'static_replace',
    'pipeline',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.

syslog_format = ("[%(name)s][env:{logging_env}] %(levelname)s "
                 "[{hostname}  %(process)d] [%(filename)s:%(lineno)d] "
                 "- %(message)s").format(
    logging_env="", hostname="")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)s %(process)d '
                      '[%(name)s] %(filename)s:%(lineno)d - %(message)s',
            },
        'syslog_format': {'format': syslog_format},
        'raw': {'format': '%(message)s'},
        },
    'handlers': {
        'console': {
            'level': 'DEBUG' if DEBUG else 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout,
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}

MITX_ROOT_URL = ''

DIRECTORIES_TO_READ = []

BROKER_URL = 'redis://localhost:6379/0'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TASK_RESULT_EXPIRES = 60 * 60 #1 hour

STATIC_ROOT = os.path.abspath(REPO_PATH / "staticfiles")
PROTECTED_DATA_ROOT = os.path.abspath(REPO_PATH / "protected_data")
NGINX_PROTECTED_DATA_URL = "/protected_data/"

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'
PROTECTED_DATA_URL = '/data/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.abspath(REPO_PATH / 'css_js_src/'),
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_JS = {
    'util' : {
        'source_filenames': [
            'js/jquery-1.9.1.js',
            'js/json2.js',
            'js/underscore.js',
            'js/backbone.js',
            'js/backbone.validations.js'
            'js/jquery.cookie.js',
            'js/bootstrap.js',
            'js/jquery-ui-1.10.2.custom.js',
            'js/jquery.flot.patched-multi.js',
            'js/jquery.flot.tooltip.js',
            'js/jquery.flot.axislabels.js',
            ],
        'output_filename': 'js/util.js',
        },
    'new_dashboard' : {
        'source_filenames': [
            'js/new_dashboard/load_analytics.js'
            ],
        'output_filename': 'js/new_dashboard.js',
        },
}

PIPELINE_CSS = {
    'bootstrap': {
        'source_filenames': [
            'css/bootstrap.css',
            'css/bootstrap-responsive.css',
            'css/bootstrap-extensions.css',
            ],
        'output_filename': 'css/bootstrap.css',
        },
    'util_css' : {
        'source_filenames': [
            'css/jquery-ui-1.10.2.custom.css',
            ],
        'output_filename': 'css/util_css.css',
    }
}

PIPELINE_DISABLE_WRAPPER = True
PIPELINE_YUI_BINARY = "yui-compressor"

PIPELINE_CSS_COMPRESSOR = None
PIPELINE_JS_COMPRESSOR = None

PIPELINE_COMPILE_INPLACE = True
PIPELINE = True

#Needed for MITX imports to work
from mitx_settings import *

override_settings = os.path.join(BASE_DIR, "override_settings.py")
if os.path.isfile(override_settings):
    execfile(override_settings)

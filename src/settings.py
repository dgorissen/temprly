# Initialize App Engine and import the default settings (DB backend, etc.).
# If you want to use a different backend you have to remove all occurences
# of "djangoappengine" from this file.
from djangoappengine.settings_base import *

from os import path
import dbindexer

SECRET_KEY = '=r5-$b*8hglm+89684&@$#%9t043hlm6-3d3vfc4((7yd0dbwrehvi'

DATABASES['native'] = DATABASES['default']
DATABASES['default'] = {'ENGINE': 'dbindexer', 'TARGET': 'native'}
AUTOLOAD_SITECONF = 'dbindexes'

# how many readings can be submitted per minute
REQ_PER_MIN = 3 

PROJECT_ROOT = path.abspath(path.dirname(__file__))
STATIC_ROOT = path.join(PROJECT_ROOT,"static" + path.sep)
STATIC_URL = '/static/'

SITE_ID = 1
SITE_URL="http://guarduino.appspot.com"

# let django know we have a user profile class
AUTH_PROFILE_MODULE = "temprly.UserProfile"

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    path.join(PROJECT_ROOT, "templates"),
)

MIDDLEWARE_CLASSES = (
    # This loads the index definitions, so it has to come first
    'autoload.middleware.AutoloadMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

DBINDEXER_BACKENDS = (
    'dbindexer.backends.BaseResolver',
    'dbindexer.backends.FKNullFix',
    'dbindexer.backends.InMemoryJOINResolver',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.redirects',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'djangotoolbox',
    'temprly',
    'autoload',
    'dbindexer',
    # djangoappengine should come last, so it can override a few manage.py commands
    'djangoappengine',
)


# This test runner captures stdout and associates tracebacks with their
# corresponding output. Helps a lot with print-debugging.
TEST_RUNNER = 'djangotoolbox.test.CapturingTestSuiteRunner'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = "login"

ADMIN_MEDIA_PREFIX = '/media/admin/'
MEDIA_ROOT = path.join(PROJECT_ROOT, 'media')
TEMPLATE_DIRS = (path.join(PROJECT_ROOT, 'templates'),)

ROOT_URLCONF = 'urls'

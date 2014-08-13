# Django settings for Observations project.

import os, sys
import platform
import site

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
import django.template
django.template.add_to_builtins('django.templatetags.future')
TEST = 'test' in sys.argv
PRODUCTION = True if platform.node().startswith('pydevsba') else False
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(CURRENT_PATH)
PREFIX="/observations" #if PRODUCTION else ""

PRODUCTION = True if platform.node().startswith('scheduler') else False
VERSION = '1.02'
TEST = 'test' in sys.argv
DEBUG = not PRODUCTION

TEMPLATE_DEBUG = DEBUG
DOMAIN = 'lcogt.net'
HOSTNAME = DOMAIN if PRODUCTION else 'localhost'
HOME = os.environ.get('HOME','/tmp')

DEV_DB_BACKEND = 'django.db.backends.mysql'
SQLITE_DB_PATH = HOME
def dev_db_name(dbname, backend):
    if 'sqlite' in backend:
        return os.path.join(SQLITE_DB_PATH, '%s.sqlite' % dbname)
    else:
        return dbname

DEFAULT_DB = {
              'ENGINE'   : 'django.db.backends.mysql' if PRODUCTION else DEV_DB_BACKEND,
              'NAME'     : 'observations' if PRODUCTION else dev_db_name('observations', DEV_DB_BACKEND),
              'USER'     : 'citsci' if PRODUCTION else 'root',
              'PASSWORD' : 'aster01d' if PRODUCTION else '',
              'HOST'     : 'db01sba' if PRODUCTION else '',
              'OPTIONS'  : {'init_command': 'SET storage_engine=INNODB'} if PRODUCTION else {},
              }
RBAUTH_DB = {
            'ENGINE'    : DEV_DB_BACKEND,
            'NAME'      : dev_db_name('rbauth', DEV_DB_BACKEND),
            'USER'      : 'root',
            'PASSWORD'  : '',
            'HOST'      : '',
            'OPTIONS'   : {'init_command': 'SET storage_engine=INNODB'} if DEV_DB_BACKEND == 'django.db.backends.mysql' else {} ,
            'TEST_DEPENDENCIES': [],
        }

if PRODUCTION:
    CACHES = {
              'default': {
                          'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
                          'LOCATION': '127.0.0.1:11211',
                          },
    }

DATABASES = {'default'      : DEFAULT_DB,
              'rbauth'      : RBAUTH_DB
            }

ADMINS = (
          ('Edward Gomez', 'egomez@lcogt.net'),
          ('Zach Walker', 'zwalker@lcogt.net'),
          ('Doug Thomas', 'dthomas@lcogt.net'),
         )
MANAGERS = ADMINS

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

if PRODUCTION:
    STATIC_ROOT = '/home/egomez/public_html/static/observations'
    STATIC_URL = 'http://lcogt.net/observations/static/'
else:
    STATIC_ROOT = '/var/www/html/static/'
    STATIC_URL = PREFIX + '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'whatsup', 'static'),]

##### Upload directory for the proposalsubmit app. Also where proposal PDFs are created
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'media')
MEDIA_URL = PREFIX + '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r7xw%%2&w)3e@p@@-=^arnh%z&j^)f_zbu_(&13!*+p-oj*4^6'

# List of callables that know how to import templates from various sources.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'b$g^1v5ib=6aid=(m*f1j-oe04=e77lzyj#yk_(*2^=!b(2pt8'


ROOT_URLCONF = 'observations.urls'

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'observations.wsgi.application'

TEMPLATE_DIRS = (
    CURRENT_PATH +'/images/templates/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'rbauth',
    'images',
)


try:
    from local_settings import *
except:
    pass



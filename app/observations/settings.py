'''
Observations: Open access archive app for Las Cumbres Observatory Global Telescope Network
Copyright (C) 2014-2015 LCOGT

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''
# Django settings for Observations project.

from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
from django.utils.crypto import get_random_string
import os
import sys
import site


TEST = 'test' in sys.argv
CURRENT_PATH = os.path.dirname(os.path.realpath(__file__))
PRODUCTION = True if CURRENT_PATH.startswith('/var/www') else False
PREFIX = os.environ.get('PREFIX', '')
BASE_DIR = os.path.dirname(CURRENT_PATH)

VERSION = '0.2'
DEBUG = True if os.environ.get('DEBUG', None) else not PRODUCTION
TEMPLATE_DEBUG = DEBUG
DOMAIN = 'lcogt.net'
HOSTNAME = DOMAIN if PRODUCTION else 'localhost'
HOME = os.environ.get('HOME', '/tmp')


DATABASES = {
    'default': {
        'NAME': os.environ.get('OBS_DB_NAME', ''),
        "USER": os.environ.get('OBS_DB_USER', ''),
        "PASSWORD": os.environ.get('OBS_DB_PASSWD', ''),
        "HOST": os.environ.get('OBS_DB_HOST', ''),
        "OPTIONS": {'init_command': 'SET storage_engine=INNODB'} if PRODUCTION else {},
        "ENGINE": "django.db.backends.mysql",
    },
    'rbauth': {
        'NAME': os.environ.get('RBAUTH_DB_NAME', ''),
        "USER": os.environ.get('RBAUTH_DB_USER', ''),
        "PASSWORD": os.environ.get('RBAUTH_DB_PASSWD', ''),
        "HOST": os.environ.get('RBAUTH_DB_HOST', ''),
        "OPTIONS": {'init_command': 'SET storage_engine=INNODB'} if PRODUCTION else {},
        "ENGINE": "django.db.backends.mysql",
    }
}

if False:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
        },
    }


ADMINS = (
    ('Edward Gomez', 'egomez@lcogt.net'),
)
MANAGERS = ADMINS

TIME_ZONE = 'Europe/London'

LANGUAGE_CODE = 'en-us'

SITE_ID = 1

USE_I18N = True

STATIC_ROOT = '/var/www/html/static/'
STATIC_URL = PREFIX + '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'images', 'static'), ]

# Upload directory
MEDIA_ROOT = os.path.join(CURRENT_PATH, 'media')
MEDIA_URL = PREFIX + '/media/'

# Make this unique, and don't share it with anybody.
chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
SECRET_KEY = get_random_string(50, chars)

# List of callables that know how to import templates from various sources.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

ALLOWED_HOSTS = ['.lco.gtn', '.lcogt.net']

ROOT_URLCONF = 'observations.urls'

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
            ]
        }
    }
]

MIDDLEWARE_CLASSES = (
    'opbeat.contrib.django.middleware.OpbeatAPMMiddleware',
    'opbeat.contrib.django.middleware.Opbeat404CatchMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)


# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'observations.wsgi.application'

FIXTURE_DIRS = (
    CURRENT_PATH + '/observations/images/fixtures/',
)

INSTALLED_APPS = (
    'opbeat.contrib.django',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'images',
)

OPBEAT = {
    'ORGANIZATION_ID': os.environ.get('OBS_OPBEAT_ORGID',''),
    'APP_ID': os.environ.get('OBS_OPBEAT_APPID',''),
    'SECRET_TOKEN': os.environ.get('OBS_OPBEAT_TOKEN',''),
    'DEBUG': DEBUG,
}

DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S +0000"
SHORT_DATETIME_FORMAT = "%a, %d %b %Y %H:%M:%S"

FITS_VIEWER_URL = 'http://data.lcogt.net/view/'

if sys.argv[1] == 'test':
    OPBEAT['APP_ID'] = None

if not PRODUCTION:
    try:
        from local_settings import *
    except:
        pass

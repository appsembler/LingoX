"""
These settings are here to use during tests, because django requires them.

In a real-world use case, apps in this project are installed into other
Django applications, so these settings will not be used.
"""

from __future__ import absolute_import, unicode_literals

from os.path import abspath, dirname, join

from django.utils.translation import ugettext_lazy as _

DEBUG = True


def root(*args):
    """
    Get the absolute path of the given path relative to the project root.
    """
    return join(abspath(dirname(__file__)), *args)


# Dummy value to emulate the Open edX site configuration helpers.
MOCK_SITE_CONFIGS = {}

# Dummy value to emulate the Open edX `ENV_TOKENS` in `aws.py`.
ENV_TOKENS = {}

# Dummy feature flags dictionary.
FEATURES = {
    'ENABLE_LINGOX': False,  # The feature is disabled by default.
}

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',

    'openedx.core.djangoapps.lang_pref.middleware.LanguagePreferenceMiddleware',
    'openedx.core.djangoapps.dark_lang.middleware.DarkLangMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',

    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'default.db',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'lingox',
    'test_site',
)

LANGUAGE_CODE = 'eo'

LOCALE_PATHS = [
    root('lingox', 'conf', 'locale'),
    root('tests', 'edx_platform_mock', 'conf', 'locale'),
]


LANGUAGES = [
    ('ar', _('Arabic')),
    ('en', _('English')),
    ('eo', _('Esperanto')),
]

ROOT_URLCONF = 'test_site.urls'

SECRET_KEY = 'insecure-secret-key'

USE_TZ = True
USE_I18N = True
USE_L10N = True

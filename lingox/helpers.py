"""
Helper functions for the LingoX module.
"""
from __future__ import absolute_import, unicode_literals

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers

LOGGER = logging.getLogger(__name__)


def add_locale_middleware(middleware_classes):
    """
    Add the LingoX's DefaultLocaleMiddleware to the MIDDLEWARE_CLASSES tuple correctly.

    Args:
        middleware_classes: The MIDDLEWARE_CLASSES tuple from the settings.
    Return:
        The new MIDDLEWARE_CLASSES with the lingox middleware.
    """
    lingox_middleware = 'lingox.middleware.DefaultLocaleMiddleware'
    site_middleware = 'django.contrib.sites.middleware.CurrentSiteMiddleware'

    if lingox_middleware in middleware_classes:
        return middleware_classes

    if not isinstance(middleware_classes, tuple):
        middleware_classes = tuple(middleware_classes)

    LOGGER.warning('Monkeypatching MIDDLEWARE_CLASSES to add DefaultLocaleMiddleware')

    other_locale_middlewares = [
        'openedx.core.djangoapps.lang_pref.middleware.LanguagePreferenceMiddleware',
        'openedx.core.djangoapps.dark_lang.middleware.DarkLangMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    ]

    # If this broke, then this module needs an update to sync with the edX Platform default middlewares.
    locale_middleware_indexes = [
        middleware_classes.index(class_name) for class_name in other_locale_middlewares
    ]

    first_locale_middleware_index = min(locale_middleware_indexes)

    sites_middleware_index = middleware_classes.index(site_middleware)

    if sites_middleware_index > first_locale_middleware_index:
        raise ImproperlyConfigured(
            # This exception indicates that this package either needs an update, or no longer compatible with the edX
            # platform sites.
            'Something is wrong with the MIDDLEWARE_CLASSES, the sites middleware was found after a locale-aware '
            'middleware. The `DefaultLocaleMiddleware` cannot work in this case. original={classes}'.format(
                classes=middleware_classes,
            )
        )

    # Insert the DefaultLocaleMiddleware before any other locale-related
    # middleware in order for it to work
    return (
        middleware_classes[:first_locale_middleware_index]
        + (lingox_middleware,)
        + middleware_classes[first_locale_middleware_index:]
    )


def is_api_request(request):
    """
    Check if the a request is targeting an API endpoint.

    Args:
        request: A django request.
    Return: True if the request is an API request and False otherwise.
    """
    default_api_prefixes = [
        '/api/',
        '/user_api/',
        '/notifier_api/',
    ]

    api_prefixes = settings.ENV_TOKENS.get('LINGOX_API_URL_PREFIXES', default_api_prefixes)

    for prefix in api_prefixes:
        if request.path.startswith(prefix):
            return True

    return False


def is_feature_enabled():
    """
    Check if the feature is enabled for the Site or for the platform as a whole.
    """
    is_enabled_in_platform = settings.FEATURES.get('ENABLE_LINGOX', False)
    return configuration_helpers.get_value('ENABLE_LINGOX', is_enabled_in_platform)

"""
Helper functions for the LingoX module.
"""
from __future__ import absolute_import, unicode_literals

import logging

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
    indexes = [
        middleware_classes.index(class_name) for class_name in other_locale_middlewares
    ]

    first_index = min(indexes)

    # Insert the DefaultLocaleMiddleware before any other locale-related middleware in order for it to work
    return middleware_classes[:first_index] + (lingox_middleware,) + middleware_classes[first_index:]


def is_api_request(request):
    """
    Check if the a request is targeting an API endpoint.

    Args:
        request: A django request.
    Return: True if the request is an API request and False otherwise.
    """
    if request.path.startswith('/api/'):
        return True
    elif request.path.startswith('/user_api/'):
        return True
    elif request.path.startswith('/notifier_api/'):
        return True

    return False

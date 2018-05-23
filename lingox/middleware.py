"""
LingoX i18n Middleware.
"""
from __future__ import absolute_import, unicode_literals

from django.conf import settings

from lingox.helpers import is_api_request


class DefaultLocaleMiddleware(object):
    """
    Change the language to `settings.LANGUAGE_CODE` for all non-API requests.

    This will force the i18n machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies.
    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    specifically django.middleware.locale.LocaleMiddleware
    """

    def process_request(self, request):
        """
        Change the request's `HTTP_ACCEPT_LANGUAGE` to `settings.LANGUAGE_CODE`.
        """
        # This middleware is only needed for regular browser pages, it's effect is breaking the behaviour on the
        # mobile apps.
        if not is_api_request(request):
            if 'HTTP_ACCEPT_LANGUAGE' in request.META:
                # Preserve the browser provided language just in case,
                # the underscore prefix means that you probably shouldn't be using it anyway
                request.META['_HTTP_ACCEPT_LANGUAGE'] = request.META['HTTP_ACCEPT_LANGUAGE']

            # Enforce LANGUAGE_CODE regardless of the browser provided language
            # Django will use this value in the LocaleMiddleware to display the desired language
            request.META['HTTP_ACCEPT_LANGUAGE'] = settings.LANGUAGE_CODE

"""
LingoX i18n Middleware.
"""
from __future__ import absolute_import, unicode_literals

from django.conf import settings

from lingox.helpers import is_api_request, is_feature_enabled
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers


class DefaultLocaleMiddleware(object):
    """
    Change the language to `settings.LANGUAGE_CODE` for all non-API requests.

    If there's a site_configuration `LANGUAGE_CODE`, that will be used instead.

    This will force the i18n machinery to always choose settings.LANGUAGE_CODE
    as the default initial language, unless another one is set via sessions or cookies.
    Should be installed *before* any middleware that checks request.META['HTTP_ACCEPT_LANGUAGE'],
    specifically django.middleware.locale.LocaleMiddleware
    """

    def patch_request(self, request):
        """
        Enforce LANGUAGE_CODE regardless of the browser provided language.

        Django will use this value in the LocaleMiddleware to display the desired language.
        """
        if 'HTTP_ACCEPT_LANGUAGE' in request.META:
            # Preserve the browser provided language just in case,
            # the underscore prefix means that you probably shouldn't be using it anyway
            request.META['_HTTP_ACCEPT_LANGUAGE'] = request.META['HTTP_ACCEPT_LANGUAGE']

        language_code = configuration_helpers.get_value('LANGUAGE_CODE', settings.LANGUAGE_CODE)
        request.META['HTTP_ACCEPT_LANGUAGE'] = language_code

    def process_request(self, request):
        """
        Change the request's `HTTP_ACCEPT_LANGUAGE` to `settings.LANGUAGE_CODE`.
        """
        # This middleware is only needed for regular browser pages.
        # It is incompatible with the mobile apps and APIs in general.
        if is_feature_enabled() and not is_api_request(request):
            self.patch_request(request)

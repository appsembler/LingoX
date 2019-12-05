# -*- coding: utf-8 -*-
"""
localizerx Django application initialization.
"""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.conf import settings

from localizerx.helpers import add_locale_middleware


class LocalizerXConfig(AppConfig):
    """
    Configuration for the localizerx Django application.
    """

    name = 'localizerx'

    def ready(self):
        """
        Monkeypatch MIDDLEWARE_CLASSES to the LocalizerX middleware.
        """
        settings.MIDDLEWARE_CLASSES = add_locale_middleware(settings.MIDDLEWARE_CLASSES)

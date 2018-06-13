# -*- coding: utf-8 -*-
"""
lingox Django application initialization.
"""

from __future__ import absolute_import, unicode_literals

from django.apps import AppConfig
from django.conf import settings

from lingox.helpers import add_locale_middleware


class LingoXConfig(AppConfig):
    """
    Configuration for the lingox Django application.
    """

    name = 'lingox'

    def ready(self):
        """
        Monkeypatch MIDDLEWARE_CLASSES to the LingoX middleware.
        """
        settings.MIDDLEWARE_CLASSES = add_locale_middleware(settings.MIDDLEWARE_CLASSES)

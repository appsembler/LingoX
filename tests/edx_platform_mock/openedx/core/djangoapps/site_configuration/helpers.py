from __future__ import absolute_import, unicode_literals

from django.conf import settings


def get_value(val_name, default=None):
    """
    Return configuration value for the key specified as name argument.

    Emulate the `get_value` helper in `openedx.core.djangoapps.site_configuration.helpers`.

    This function reads whatever in `MOCK_SITE_CONFIGS`, whether it's provided in test_settings.py or
    via `@override_settings()` test helper.
    """
    return settings.MOCK_SITE_CONFIGS.get(val_name, default)

# -*- coding: utf-8 -*-
"""
Tests for LingoX.
"""
from __future__ import absolute_import, unicode_literals

import ddt
from mock import patch

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import RequestFactory, TestCase, override_settings

from lingox.helpers import add_locale_middleware, is_api_request, is_feature_enabled
from lingox.middleware import DefaultLocaleMiddleware

# The disable below because pylint is not recognizing request.META.
# pylint: disable=no-member


LINGOX_MIDDLEWARE = 'lingox.middleware.DefaultLocaleMiddleware'
SITE_MIDDLEWARE = 'django.contrib.sites.middleware.CurrentSiteMiddleware'

UNMODIFIED_MIDDLEWARE_CLASSES = [
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
]


@ddt.ddt
class SettingsTest(TestCase):
    """
    Sanity checks for the settings related to the lingox module.
    """

    def test_if_enabled(self):
        """
        Ensure that the app is enabled.
        """
        assert 'lingox' in settings.INSTALLED_APPS, 'The app should be installed by default in test.'
        assert not settings.FEATURES['ENABLE_LINGOX'], 'The app should be disabled by default in test.'

    def test_middleware_should_exists(self):
        """
        Ensure that the middleware is available through the add_locale_middleware class.
        """
        assert LINGOX_MIDDLEWARE in settings.MIDDLEWARE_CLASSES

    def test_synced_constants(self):
        """
        Ensure `UNMODIFIED_MIDDLEWARE_CLASSES` and `MIDDLEWARE_CLASSES` are in sync.
        """
        middleware_classes = [
            class_name for class_name in settings.MIDDLEWARE_CLASSES
            if class_name != LINGOX_MIDDLEWARE
        ]

        assert middleware_classes == UNMODIFIED_MIDDLEWARE_CLASSES


@ddt.ddt
class DefaultLocaleMiddlewareTest(TestCase):
    """
    Unit and integration tests for the DefaultLocaleMiddleware.
    """

    middleware_classes = add_locale_middleware(UNMODIFIED_MIDDLEWARE_CLASSES)

    def setUp(self):
        """
        Set up the environment for the test case.
        """
        super(DefaultLocaleMiddlewareTest, self).setUp()

        self.middleware = DefaultLocaleMiddleware()
        self.request_factory = RequestFactory()

    @override_settings(LANGUAGE_CODE='eo', FEATURES={'ENABLE_LINGOX': True})
    def test_non_api_views(self):
        """
        Test the middleware on non-API pages.
        """
        req = self.request_factory.get('/dummy/')
        req.META['HTTP_ACCEPT_LANGUAGE'] = 'en'
        self.middleware.process_request(req)

        assert req.META['HTTP_ACCEPT_LANGUAGE'] == 'eo',  \
            'The middleware is installed so it should change the language for non-API views.'

        assert req.META['_HTTP_ACCEPT_LANGUAGE'] == 'en',  \
            'Should preserve the original language in another META variable.'

    @ddt.data('/api/', '/user_api/')
    @override_settings(LANGUAGE_CODE='ar', FEATURES={'ENABLE_LINGOX': True})
    def test_api_views(self, api_url):
        """
        Ensure that the middleware doesn't change the non-API pages.
        """
        req = self.request_factory.get(api_url)
        client_language = 'en'
        req.META['HTTP_ACCEPT_LANGUAGE'] = client_language
        self.middleware.process_request(req)

        assert req.META['HTTP_ACCEPT_LANGUAGE'] == client_language,  \
            'The middleware is being used but it should NOT change the language for API views.'

    @ddt.data(
        {
            'settings_lang': 'en',
            'request_lang': 'eo',
            'site_configs': {},
            'expected': 'Hello World',
            'unexpected': 'Héllö Wörld',
            'message': 'The site-wide language should be used instead of the request\'s.',
        },
        {
            'settings_lang': 'eo',
            'request_lang': 'en',
            'site_configs': {},
            'expected': 'Héllö Wörld',
            'unexpected': 'Hello World',
            'message': 'The site-wide language should be used instead of the request\'s.',
        },
        {
            'settings_lang': 'eo',
            'request_lang': 'eo',
            'site_configs': {
                'LANGUAGE_CODE': 'en',
            },
            'expected': 'Hello World',
            'unexpected': 'Héllö Wörld',
            'message': 'The "Microsite" language should be used instead.',
        },
        {
            'settings_lang': 'en',
            'request_lang': 'en',
            'site_configs': {
                'LANGUAGE_CODE': 'eo',
            },
            'expected': 'Héllö Wörld',
            'unexpected': 'Hello World',
            'message': 'The "Microsite" language should be used instead.',
        },
    )
    def test_enabled_middleware_in_request(self, data):
        """
        Test different combinations of LANGUAGE_CODE and Accept-Language.

        The response language should always respect the `settings_lang` and ignore the `request_lang`.

        If `openedx.core.djangoapps.site_configuration.helpers.get_value('LANGUAGE_CODE') is available`, that should
        override the settings.LANGUAGE_CODE.
        """
        overrides = {
            'LANGUAGE_CODE': data['settings_lang'],
            'MOCK_SITE_CONFIGS': data['site_configs'],
            'FEATURES': {
                'ENABLE_LINGOX': True
            },
            'MIDDLEWARE_CLASSES': self.middleware_classes,
        }
        with override_settings(**overrides):
            res = self.client.get('/', HTTP_ACCEPT_LANGUAGE=data['request_lang'])

            msg_prefix = 'Incorrect language detected - {message}'.format(message=data['message'])
            self.assertNotContains(res, data['unexpected'], msg_prefix=msg_prefix)
            self.assertContains(res, data['expected'], msg_prefix=msg_prefix)


@ddt.ddt
class IsFeatureEnabledHelperTest(TestCase):
    """
    Tests for the `is_feature_enabled` helper function.
    """

    middleware_classes = add_locale_middleware(UNMODIFIED_MIDDLEWARE_CLASSES)

    @ddt.data({
        'features': {
            'ENABLE_LINGOX': True,
        },
        'site_configs': {},
        'expected': True,
        'message': 'Enabled via platform flag',
    }, {
        'features': {},
        'site_configs': {
            'ENABLE_LINGOX': True,
        },
        'expected': True,
        'message': 'Enabled via site configs',
    }, {
        'features': {
            'ENABLE_LINGOX': True,
        },
        'site_configs': {
            'ENABLE_LINGOX': False,
        },
        'expected': False,
        'message': 'Disabled via site configs',
    }, {
        'features': {},
        'site_configs': {},
        'expected': False,
        'message': 'Disabled by default',
    })
    def test_is_enabled_method(self, data):
        """
        Tests for the `is_feature_enabled` method.
        """
        overrides = {
            'MOCK_SITE_CONFIGS': data['site_configs'],
            'FEATURES': data['features'],
        }

        with override_settings(**overrides):
            assert is_feature_enabled() == data['expected'], data['message']

    @ddt.data({
        'is_feature_enabled': True,
        'site_configs': {},
        'expected': 'Héllö Wörld',
        'unexpected': 'Hello World',
        'message': 'Enabled, so site lang (eo) should be USED and req lang (en) should be IGNORED',
    }, {
        'is_feature_enabled': False,
        'unexpected': 'Héllö Wörld',
        'expected': 'Hello World',
        'message': 'Disabled, so site lang (eo) should be IGNORED and req lang (en) should be USED',
    })
    @override_settings(MIDDLEWARE_CLASSES=middleware_classes, LANGUAGE_CODE='eo')
    def test_feature_flags(self, data):
        """
        Test different combinations of feature flags.
        """
        with patch(
            target='lingox.middleware.is_feature_enabled',
            return_value=data['is_feature_enabled'],
        ):
            from lingox.middleware import is_feature_enabled as patched_is_feature_enabled
            assert patched_is_feature_enabled() == data['is_feature_enabled']
            res = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en')

        msg_prefix = 'Incorrect language detected - {message}'.format(message=data['message'])
        self.assertNotContains(res, data['unexpected'], msg_prefix=msg_prefix)
        self.assertContains(res, data['expected'], msg_prefix=msg_prefix)


@ddt.ddt
class APIRequestHelperTest(TestCase):
    """
    Test cases for the API request helper of lingox module.
    """

    def setUp(self):
        """
        Initialize the request factory.
        """
        super(APIRequestHelperTest, self).setUp()
        self.request_factory = RequestFactory()

    @ddt.unpack
    @ddt.data(
        {'path': '/api/', 'should_be_api': True},
        {'path': '/dashboard', 'should_be_api': False},
        {'path': '/', 'should_be_api': False},
        {'path': '/user_api/', 'should_be_api': True},
        {'path': '/notifier_api/', 'should_be_api': True},
        {'path': '/api/discussion/', 'should_be_api': True},
        {'path': '/reporting/api/', 'should_be_api': False},  # By default, LingoX don't know about reporting
    )
    def test_default_api_endpoints(self, path, should_be_api):
        """
        Tests the `is_api_request` helper on the default configuration.
        """
        assert is_api_request(self.request_factory.get(path)) == should_be_api

    @override_settings(ENV_TOKENS={
        'LINGOX_API_URL_PREFIXES': [
            '/api/',
            '/reporting/api/',
        ]
    })
    @ddt.unpack
    @ddt.data(
        {'path': '/', 'should_be_api': False},  # Still falsey
        {'path': '/api/', 'should_be_api': True},  # Custom configuration should replicate the default
        {'path': '/user_api/', 'should_be_api': False},  # Can be configured to ignore default's configurations.
        {'path': '/reporting/api/', 'should_be_api': True},  # LingoX's now recognizes /reporting/api
    )
    def test_endpoints_from_configs(self, path, should_be_api):
        """
        Tests the `is_api_request` helper on the customized configuration.
        """
        assert is_api_request(self.request_factory.get(path)) == should_be_api


@ddt.ddt
class MiddlewareAdderHelperTest(TestCase):
    """
    Tests for add_locale_middleware helper.
    """

    edx_middlewares = (
        'openedx.core.djangoapps.lang_pref.middleware.LanguagePreferenceMiddleware',
        'openedx.core.djangoapps.dark_lang.middleware.DarkLangMiddleware',
        'django.middleware.locale.LocaleMiddleware',
    )

    @ddt.data(*edx_middlewares)
    def test_missing_middleware_on_update(self, middleware_to_remove):
        """
        Ensure that the helper fails explicitly when an expected middleware is missing.
        """
        middleware_classes = tuple(
            class_name for class_name in UNMODIFIED_MIDDLEWARE_CLASSES
            if class_name != middleware_to_remove
        )

        with self.assertRaises(ValueError):
            add_locale_middleware(middleware_classes)

    def test_missing_site_middleware(self):
        """
        The helper should require the CurrentSiteMiddleware to be available in the middleware classes list.
        """
        middleware_classes = tuple(
            class_name for class_name in UNMODIFIED_MIDDLEWARE_CLASSES
            if class_name != SITE_MIDDLEWARE
        )

        with self.assertRaises(ValueError):
            add_locale_middleware(middleware_classes)

    def test_incorrect_site_middleware_location(self):
        """
        Ensure the helper complains about bizarre middleware configs.

        DefaultLocaleMiddleware can only work _after_ the CurrentSiteMiddleware
        and _before_ every locale-aware middleware.
        """
        middleware_classes = [
            'django.contrib.auth.middleware.SessionAuthenticationMiddleware',

            'openedx.core.djangoapps.lang_pref.middleware.LanguagePreferenceMiddleware',

            # After a locale-middleware, to confuse the helper
            'django.contrib.sites.middleware.CurrentSiteMiddleware',

            'openedx.core.djangoapps.dark_lang.middleware.DarkLangMiddleware',
            'django.middleware.locale.LocaleMiddleware',
            'django.middleware.common.CommonMiddleware',
        ]

        with self.assertRaises(ImproperlyConfigured):
            add_locale_middleware(middleware_classes)

    @ddt.data(*edx_middlewares)
    def test_middleware_order(self, other_middleware):
        """
        Ensures that the middleware comes before any other locale-related middleware.
        """
        updated_middlewares = add_locale_middleware(UNMODIFIED_MIDDLEWARE_CLASSES)

        lingx_index = updated_middlewares.index(LINGOX_MIDDLEWARE)
        other_index = updated_middlewares.index(other_middleware)
        assert lingx_index < other_index,  \
            'DefaultLocaleMiddleware should come before any other locale-related middleware'

    def test_call_update_middleware_twice(self):
        """
        Ensure that the method works well if it was called twice.
        """
        once = add_locale_middleware(UNMODIFIED_MIDDLEWARE_CLASSES)
        twice = add_locale_middleware(add_locale_middleware(UNMODIFIED_MIDDLEWARE_CLASSES))
        assert once == twice

    @ddt.data(
        UNMODIFIED_MIDDLEWARE_CLASSES,
        tuple(UNMODIFIED_MIDDLEWARE_CLASSES),
    )
    def test_middleware_type(self, middlewares):
        """
        Ensure that the method works regardless whether the MIDDLEWARE_CLASSES was a list or a tuple.
        """
        assert isinstance(add_locale_middleware(middlewares), tuple),  \
            'Should convert to list, regardless of the input.'

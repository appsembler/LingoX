LingoX
======

|travis-badge| |codecov-badge|

An app to enforce a default language for the edX Platform regardless of browser language,
while still allowing individual learners to change their language preference.

Overview
--------

By default Django sites including the edX Platform use ``LocaleMiddleware``
to serve localized pages to the users based on their browser language.
The browser language is advertised using the ``Accept-Language`` HTTP header.

For a huge number of users this is far from correct, since it's not uncommon for users to
use an English browser interface yet expect your site to be Arabic. This is especially
true for Arabic sites. Some sites are offered in a single, other than English, language only.

This package helps to enforce ``settings.LANGUAGE_CODE`` (or ``site_configuration`` provided
value) as the site's default language for the edX Platform.
This package does allow learners to change the language. This package
also maintains backward compatibility with API endpoints and passes the ``Accept-Language``
header as-is.


How to Install
--------------

Disclaimer
  If you're looking to have a single language (e.g. French), for the edX Platform
  and a single language only i.e no English at all, even in ``/admin``, probably this app is not required.
  However, often it is required to have a default language (e.g. Arabic) for the site,
  while still being able to default to English
  or another language when needed.

The middleware that is available in this package has a rough relationship with edX's Dark Lang app.
Luckily, if we configure the Dark Lang properly, both can play nicely. To configure Dark Lang properly you need
to do either of:

- Configure Open edX ``dark_lang`` to include all the languages that you'd like to display, or
- Disable ``dark_lang`` app, through the edX Platform LMS Django Admin.

You can read more on the
`Dark Lang <https://github.com/edx/edx-platform/wiki/Internationalization-and-localization#releasing-a-language>`_
feature. But mostly it's a configuration model in the admin panel available under ``/admin/dark_lang/``.

Next, install LingoX and configure it:

- ``$ pip install -e git+https://github.com/appsembler/LingoX.git#egg=lingox``
- Add ``lingox`` to the ``ADDL_INSTALLED_APPS`` in the ``lms.env.json`` (or your ``server-vars.yml``)
- Set ``LANGUAGE_CODE`` to ``ar``
- Reload the server
- Open a new incognito window on ``http://localhost:8000/``, you should see an Arabic interface

- **Optional:** Few deployments uses the Django Sites framework (aka Microsites). If your deployment uses this framework you can still configure a different language for a specific site: go to Sites
  Configuration ``/admin/site_configuration/siteconfiguration/``, add a ``LANGUAGE_CODE`` key with the desired
  site-specific value to the site's configuration JSON.

Support Custom API Endpoints
  To retain compatibility with the mobile applications, LingoX will avoid tampering the
  ``Accept-Language`` header of any URL with the following prefixes:
  - ``/api/``
  - ``/user_api/``
  - ``/notifier_api/``

  However, different apps can introduce different API endpoints that are not covered, when needed LingoX can be
  configured to filter different prefixes with the ``LINGOX_API_URL_PREFIXES`` setting in the ``lms.env.json``
  (or ``EDXAPP_ENV_EXTRA.LINGOX_API_URL_PREFIXES`` in ``server-vars.yml``).

Monkey Patching
---------------
This module monkey-patches the edX platform the following way:

- Add the ``DefaultLocaleMiddleware`` to ``MIDDLEWARE_CLASSES`` before any *known* locale-aware middleware.
- The middleware overrides the ``Accept-Language`` header with
  ``site_configuration.helpers.get_value('LANGUAGE_CODE')`` or ``settings.LANGUAGE_CODE`` when the former is not
  available.

How to Develop
--------------
This is mostly a standard `Open edX django cookie cutter app <https://github.com/edx/cookiecutter-django-app>`_.
To start development or run the tests locally, first the environment must be prepared:

.. code-block:: bash

   $ mkvirtualenv lingox
   $ make requirements
   $ make quality
   $ make test

To run the local development server:

.. code-block:: bash

   $ python manage.py migrate
   $ python manage.py runserver



License
-------

The code in this repository is licensed under the MIT License unless
otherwise noted.

Please see ``LICENSE.txt`` for details.

The original code was developed at `Edraak <https://github.com/Edraak/edraak-platform/pull/38>`_ and used to be
licensed with AGPL 3.0. This repo has been re-licensed to MIT after Edraak's permission.

How To Contribute
-----------------

Contributions are very welcome. We're happy to accept pull requests.
TravisCI will check your code for you, and we should have a reviewer
in a couple of days.

Reporting Security Issues
-------------------------

Please do not report security issues in public. Please email security@appsembler.org.


.. |travis-badge| image:: https://travis-ci.org/appsembler/lingox.svg?branch=master
    :target: https://travis-ci.org/appsembler/lingox
    :alt: Travis

.. |codecov-badge| image:: http://codecov.io/github/appsembler/lingox/coverage.svg?branch=master
    :target: http://codecov.io/github/appsembler/lingox?branch=master
    :alt: Codecov

.. |license-badge| image:: https://img.shields.io/github/license/appsembler/lingox.svg
    :target: https://github.com/appsembler/lingox/blob/master/LICENSE.txt
    :alt: License

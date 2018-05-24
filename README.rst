LingoX
======

|travis-badge| |codecov-badge|

An app to enforce a default language for the edX Platform regardless of browser language.

Overview
--------

The edX Platform and other Django-based is bundled by default with ``LocaleMiddleware``
which aims to server localized pages to the users based on their browser language
which is advertised with the ``Accept-Language`` header.

For a huge number of users this is far from correct, since it's not uncommon for users to
use an English browser interface yet expect your site to be Arabic. This is especially
true for Arabic sites. Some sites are offered in a single, other than English, language only.

This package helps to enforce ``settings.LANGUAGE_CODE`` as the site's default language for
the edX Platform, while still allowing learners to change the language. This package
also maintains backward compatibility with API endpoints and pass the ``Accept-Language``
header as-is.


How to Install
--------------

- ``$ pip install -e git+git@github.com:appsembler/LingoX.git#egg=lingox``
- Add ``lingox`` to the ``ADDL_INSTALLED_APPS`` in the ``lms.env.json`` (or your ``server-vars.yml``)
- Set ``LANGUAGE_CODE`` to ``ar``
- Reload the server
- Open a new incognito window on ``http://localhost:8000/``, you should see an Arabic interface


Monkey Patching
---------------
This module monkey-patches the edX platform the following way:

- Add the ``DefaultLocaleMiddleware`` to ``MIDDLEWARE_CLASSES`` before any *known* locale-aware middleware
- The middleware overrides the ``Accept-Language`` header with ``settings.LANGUAGE_CODE``


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

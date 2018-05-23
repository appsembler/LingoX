from __future__ import absolute_import, unicode_literals

from django.http.response import HttpResponse
from django.utils.translation import ugettext as _


def api(request):
    return HttpResponse('{}', content_type='text/json')


def home(request):
    body = '<h1>{text}</h1>'.format(text=_('Hello World!'))
    return HttpResponse(body, content_type='text/html')

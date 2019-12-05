"""
URLs for localizerx.
"""
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from test_site import views

urlpatterns = [
    url(r'^api/$', views.api),
    url(r'^user_api/$', views.api),
    url(r'^notifier_api/$', views.api),

    url(r'^reporting/api/$', views.api),

    url(r'^dashboard/$', views.home),
    url(r'^$', views.home),
]

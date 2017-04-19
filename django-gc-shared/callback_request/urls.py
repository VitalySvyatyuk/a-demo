# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns(
    'callback_request.views',
    url('^$', 'callback_request',
        name="callback_request_page"),
)

# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns

urlpatterns = patterns("platforms.views",
                       url(r'^$', 'quotes_info',
        name='mt4_quotes_info'),
                       )

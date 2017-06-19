# coding=utf-8
from django.conf.urls import *

urlpatterns = patterns(
    'visitor_analytics.views',
    url('^utm/$', 'utm_report',
        name='visitor_analytics_utm_report'),
)

# coding=utf-8
from django.conf.urls import *

urlpatterns = patterns('notification.views',
    url('^view/(?P<notification_id>\d+)/$', 'view_notification', name='viewnotification')
    )
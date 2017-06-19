# coding=utf-8
from django.conf.urls import *


urlpatterns = patterns('massmail.views',
    url('^unsubscribe_user/(?P<signature>\w+)/(?P<campaign_id>\d+)/(?P<email>.+)$', 'unsubscribe',
        name='massmail_unsubscribe_email_id'),
    url('^unsubscribe_user/(?P<signature>\w+)/(?P<email>.+)$', 'unsubscribe',
        name='massmail_unsubscribe_email'),
    url('^unsubscribe/(?P<email>[^/]+)/(?P<signature>\w+)/$', 'unsubscribe'),
    url('^unsubscribe/(?P<email>[^/]+)/(?P<signature>\w+)/(?P<campaign_id>\d+)/$', 'unsubscribe'),
    url('^unsubscribed/(?P<email>[^/]+)/$', 'unsubscribed',
        name='massmail_unsubscribed'),
    url('^unsubscribed/(?P<email>[^/]+)/(?P<campaign_id>\d+)/$', 'unsubscribed',
        name='massmail_unsubscribed_id'),
    url('^resubscribe/(?P<email>[^/]+)/$', 'resubscribe',
        name='massmail_resubscribe'),
    url('^resubscribe/(?P<email>[^/]+)/(?P<campaign_id>\d+)/$', 'resubscribe',
        name='massmail_resubscribe_id'),
)

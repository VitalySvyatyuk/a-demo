# coding=utf-8
import os.path

from django.conf.urls import *
from django.conf import settings

urlpatterns = patterns('massmail.views',
    url('^view/(?P<campaign_id>\d+)/$', 'view_campaign',
        name='massmail_view_campaign'),
    url('^serve/(?P<path>.*)$', 'serve_static',
        {"document_root": os.path.join(settings.STATIC_ROOT, 'img')}),
)

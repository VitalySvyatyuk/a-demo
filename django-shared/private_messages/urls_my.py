# This is a copy of messages.urls but with changed username regex

from django.conf.urls import *
from django.views.generic import RedirectView

from private_messages.views import *

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='inbox/')),
    url(r'^inbox/$', inbox, name='messages_inbox'),
    url(r'^outbox/$', outbox, name='messages_outbox'),
    url(r'^compose/$', compose, name='messages_compose'),
#    url(r'^compose/(?P<recipient_id>[\d]+)/$', compose, name='messages_compose_to'),
    url(r'^reply/(?P<message_id>[\d]+)/$', reply, name='messages_reply'),
    url(r'^view/(?P<message_id>[\d]+)/$', view, name='messages_detail'),
    url(r'^delete/(?P<message_id>[\d]+)/$', delete, name='messages_delete'),
    url(r'^undelete/(?P<message_id>[\d]+)/$', undelete, name='messages_undelete'),
    url(r'^mark_as/(?P<mode>[\w_]*)$', mark_as, name='messages_mark_as'),
    url(r'^trash/$', trash, name='messages_trash'),
)
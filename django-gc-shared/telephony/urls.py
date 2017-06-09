# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns('telephony.views',
    url(r'^api/manager_by_client_num/(?P<phone>.+)$', 'manager_by_client_num', name="telephony_manager_by_client_num"),
    url(r'^api/records_by_user/(?P<uid>\d+)$', 'records_by_user', name="telephony_records_by_user"),
    url(r'^api/vm_records_by_user/(?P<uid>\d+)$', 'voicemail_records_by_user'),

    url(r'^calls/ajax$', 'calls_ajax', name='telephony_calls_ajax'),
    url(r'^call/(?P<external_id>\d+)/(?P<call_id>\d+)$', 'call', name='telephony_call'),


    url(r'^calls/(?P<user_id>\d+)/ajax$', 'calls_by_user_ajax', name='telephony_calls_by_user_ajax'),
    url(r'^vmcalls/(?P<user_id>\d+)/ajax$', 'vmcalls_by_user_ajax', name='telephony_vmcalls_by_user_ajax'),
)

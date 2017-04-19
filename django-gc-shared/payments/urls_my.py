# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns("payments.views",

    # Ajax views
    url(r'^ajax/withdrawrequest_data/$', 'request_data', {"operation": "withdraw"},
        name='payments_ajax_withdrawrequest_data'),

    url(r'^ajax/baserequest_data/$', 'request_data', {"operation": "base"},
        name='payments_ajax_baserequest_data'),

    url(r'^ajax/depositrequest_data/$', 'request_data', {"operation": "deposit"},
        name='payments_ajax_depositrequest_data'),

    url(r'^ajax/withdrawrequest_update/$', 'request_update', {"operation": "withdraw"},
        name='payments_ajax_withdrawrequest_update'),

    url(r'^ajax/depositrequest_update/$', 'request_update', {"operation": "deposit"},
        name='payments_ajax_depositrequest_update'),


    ##################################################
    #Payments callback urls
    url("^accounts/(?P<operation>deposit|withdraw)/(?:(?P<object_id>\d+)/)?(?P<status>success|fail)/$",
        "operation_status",
        name="payments_operation_status"),

    url("^accounts/deposit/(?:(?P<object_id>\d+)/)?result/?$",
        "operation_result",
        name="payments_operation_result"),

    ##################################################
    #@staff_member_required
    url(r'^requisit/(?P<request_id>\d+)/modal/$',
        "requisit_view_modal",
        name="payments_requisit_view_modal"),

    url(r'^requests/withdraw/group/(?P<group_id>\d+)/$',
        "account_withdraw_requests_group",
        name="payments_account_withdraw_requests_group"),

    url(r'^requests/withdraw/decline/(?P<request_id>\d+)/modal$',
        "withdraw_request_decline_modal",
        name="payments_withdraw_request_decline_modal"),

    url(r'^make_transaction$',
        "make_any_transaction",
        name="payments_any_transaction"),

    url(r'^export_card_withdrawals$', "export_card_withdrawals", name="payments_export_card_withdrawals")
)

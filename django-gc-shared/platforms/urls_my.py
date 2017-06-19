# -*- coding: utf-8 -*-

from django.conf.urls import url, patterns, include
from platforms.views import CreateAccountView, CreateAccountModalView

urlpatterns = patterns("platforms.views",
                       url("^$", 'account_list',
        name="mt4_account_list"),


                       url("^create/$", CreateAccountModalView.as_view(),
        name="mt4_create"),
                       url("^create/$", CreateAccountModalView.as_view(),
        name="mt4_create_account"),


                       url("^ajax/create/(?P<slug>[a-zA-z0-9_]+)?$", CreateAccountView.as_view(),
        name="mt4_process_create_account"),

                       url("^get_ib_accounts/$", "get_ib_accounts",
        name="mt4_get_ib_accounts"),



                       # url("^get_form/(?P<slug>[a-zA-z0-9_]+)$", "get_form",
    #     name="mt4_get_form"),
    # url("^process_create/$", "process_create_account",
    #     name="mt4_process_create_account"),
    url("^get_welcome_page/$", "get_account_welcome_page",
        name="mt4_get_welcome_page"),



                       url("^create/(?P<slug>[a-zA-z0-9_]+)/$", "create_account",
        name="mt4_create_account"),
                       url("^verify_docs/$", "verify_docs", name="verify_docs"),

                       url("^mobile_create/(?P<slug>[a-zA-z0-9_]+)/$", "create_account",
        {'extra_context': {'mobile': True}}, name="mt4_create_account_mobile"),
                       url("^(?P<account_id>\d+)/change_leverage/$", "change_leverage",
        name="mt4_change_leverage"),
                       url("^(?P<account_id>\d+)/restore_from_archive/$", "restore_from_archive",
        name="mt4_restore_from_archive"),
                       url("^(?P<account_id>\d+)/history/$", "account_history",
        name="mt4_account_history"),
                       url("^(?P<account_id>\d+)/password_recovery/$", "password_recovery",
        name="mt4_password_recovery"),
                       url("^(?P<account_id>\d+)/reports/", include("reports.urls_my")),

                       # urls to get account balance
    url("^balance/$", "balance",
        name="mt4_account_balance"),
                       url("^(?:(?P<account_id>\d+)/)?agent_list/$", "agent_list",
        name="mt4_agent_list"),
                       url("^(?:(?P<slug>\w+)/)welcome/(?P<account_id>\d+)/(?:(?P<user_id>\d+)/)?$",
        "welcome_account",
        name="mt4_account_welcome"),
                       url("^waiting/(?P<task_id>.*)$",
        "wait_for_account_creation",
        name="mt4_wait_for_account_creation"),
                       url("^account_info/(?P<acc_id>\d+)?$",
        "account_info",
        name="mt4_account_info"),
                       url(r'^ajax/account_creation_done/(?P<task_id>[a-z0-9-]+)$', 'ajax_account_creation_done',
        name='mt4_ajax_account_creation_done'),
                       )

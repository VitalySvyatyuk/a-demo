# coding: utf-8
from django.conf.urls import *

urlpatterns = patterns('crm.views',

    # dashboard
    url(r'^ajax/next_notify$', 'retrieve_next_notification', name="crm_retrieve_next_notification"),

    url(r'^dashboard$', 'dashboard', name="crm_dashboard"),
    url(r'^viewlogs/ajax$', 'viewlogs_ajax', name="crm_viewlogs_ajax"),

    url(r'^search/ajax$', 'search_ajax', name="crm_search_ajax"),
    url(r'^user/more/ajax$', 'user_more_ajax', name="crm_user_more_ajax"),
    url(r'^user/(?P<user_id>\d+)/survey$', 'survey_page', name="crm_survey_page"),
    url(r'^user/(?P<user_id>\d+)/page$', 'user_page', name="crm_user_page"),

    url(r'^user/(?P<user_id>\d+)/logs/ajax$', 'logs_by_user_ajax', name="crm_logs_by_user_ajax"),
    url(r'^user/(?P<user_id>\d+)/paymentrequests/deposit/ajax$', 'user_deposit_requests_ajax', name="crm_user_deposit_requests_ajax"),
    url(r'^user/(?P<user_id>\d+)/paymentrequests/withdraw/ajax$', 'user_withdraw_requests_ajax', name="crm_user_withdraw_requests_ajax"),


    # chat
    url(r'^snapengage_handler$', 'snapengage_handler', name="crm_snapengage_handler"),

    # service
    url(r'^reassign/(?P<user_id>\d+)$', 'change_user_manager', name="crm_change_user_manager"),

    # asterisk helpers
    url(r'^api/uid_by_phone/(?P<phone>.+)$', 'uid_by_phone', name="crm_uid_by_phone"),

    # old
    url(r'^$', 'frontpage',  name="crm_frontpage"),
    url(r'^by_manager/(?P<manager_username>[^/]+)/?$', 'frontpage', name="crm_frontpage_by_manager"),
    url(r'^by_agent_code/(?P<agent_code>\d+)/?$', 'frontpage', name="crm_frontpage_by_agent_code"),
    url(r'^broco/$', 'frontpage', kwargs={'broco':True},  name="broco_crm_frontpage"),
    url(r'^broco/by_manager/(?P<manager_username>[^/]+)/?$', 'frontpage', kwargs={'broco':True},
        name="broco_crm_frontpage_by_manager"),
    url(r'^broco/by_agent_code/(?P<agent_code>\d+)/?$', 'frontpage', kwargs={'broco':True},
        name="broco_crm_frontpage_by_agent_code"),
    url(u'^reception/$', 'reception_call_form', name="crm_reception_call_form"),
    url(u'^financial_department/$', 'financial_dpt_call_form', name="crm_financial_dpt_call_form"),
    url(r'^ajax/save/call$', 'save_call', name="crm_save_call_ajax"),
    url(r'^ajax/save/comment$', 'save_comment', name="crm_save_comment_ajax"),
    url(r'^ajax/load/call$', 'load_calls', name="crm_call_list_ajax"),
    url(r'^ajax/save/planned_call$', 'save_planned_call', name="crm_save_planned_call_ajax"),
    url(r'^ajax/save/link_request$', 'save_link_request', name="crm_save_link_request_ajax"),
    url(r'^ajax/save/new_customer_result$', 'save_call', {'new_customer': True}, name="crm_save_new_customer_result_ajax"),
    url(r'^ajax/load/account_info$', 'load_account_info', name="crm_load_account_info_ajax"),
    url(r'^ajax/load/account_data$', 'load_account_data', name="crm_load_account_data_ajax"),
    url(r'^ajax/load/new_customer_data$', 'load_account_data', {'new_customer': True}, name="crm_load_new_customer_data_ajax"),
    url(r'^ajax/load/manager_data$', 'load_manager_data', name="crm_load_manager_data_ajax"),
)

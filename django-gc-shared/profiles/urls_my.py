# -*- coding: utf-8 -*-

from django.conf.urls import *

from django.contrib.auth import views as auth_views


urlpatterns = patterns("profiles.views",
    url(r"^my/$", "profile_my",
        name="profiles_my"),
    url(r"^create/$", "create_profile",
        name="profiles_create_profile"),
    url(r"^upload_avatar/$", "upload_avatar",
        name="profiles_upload_avatar"),
    # url(r"^edit/$", "edit_profile",
    #     name="profiles_edit_profile"),
    url(r"^edit/send_confirmation_email/$", "edit_email",
        name="profiles_edit_email"),

    url(r'^verify_document/(?P<issue_id>\w+)/$', 'verify_document', name='verify_document'),

    url(r'^watch_document/(?P<issue_id>\w+)/$', 'watch_document', name='watch_document'),

    url(r"^new_messages/$", "new_messages",
        name="profiles_new_messages"),

    url(r"^(?P<username>[ \w.@+-]+)/confirm/(?P<field>\w+)/(?:(?P<status>[tfc])/)?$", "confirm_field",
        name="profiles_confirm_field"),
    url(r"^reset_otp/(?P<profile_id>\d+)/$", "reset_otp", name="profiles_reset_otp"),

    url(r"switch_document_status/(?P<profile_id>\d+)/$", 'switch_documents_status', name='switch_documents_status'),

    url(r"^(?P<username>[ \w.@+-]+)/$", "profile_detail",
        name="profiles_profile_detail"),
    url(r"^(?P<username>[ \w.@+-]+)/edit/$", "edit_profile",
        name="profiles_edit_profile"),

    url(r'^password/change/$', "password_change",
        {"template_name": "profiles/change_password.html"},
        name='auth_password_change'),
    url(r'^password/change/done/$', auth_views.password_change_done,
        {"template_name": "profiles/change_pass_done.html"},
        name='auth_password_change_done'),

#    url("^documents/upload/$", "upload_document",
#        name="profiles_upload_document"),
    url('^unsubscribe_user/(?P<signature>\w+)/(?P<campaign_id>\w+)/(?P<email>.+)$',
        'unsubscribe_form',
        name='profile_unsubscribe'),
    # Compatibility with older emails already sent
    url('^unsubscribe/(?P<email>[^/]+)/(?P<signature>\w+)/(?P<campaign_id>\w+)/$',
        'unsubscribe_form'),

)

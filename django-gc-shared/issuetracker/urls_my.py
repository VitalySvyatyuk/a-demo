# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns("issuetracker.views",
    url(r"^create/$", "issue_create",
        name="issuetracker_issue_create"
    ),
    url(r"^list/$", "user_issue_list",
        name="issuetracker_issue_list"
    ),
    url(r"^(?P<issue_id>\d+)/$", "issue_detail",
        name="issuetracker_issue_detail"
    ),
    url(r"^(?P<issue_id>\d+)/add_comment/$", "add_comment",
        name="issuetracker_add_comment"
    ),
    url(r"^(?P<issue_id>\d+)/add_attachment/$", "add_attachment",
        name="issuetracker_add_attachment"
    ),

    url(r"^statistics/$", 'statistics_dashboard', name="dashboard_statistics"),
    url(r"^statistics/get/$", "get_statistics", name="issue_statistic"),
)

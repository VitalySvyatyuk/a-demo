# -*- coding: utf-8 -*-
from django.conf.urls import *

urlpatterns = patterns("issuetracker.views",
    url(r"^statistics/$", 'statistics_dashboard', name="dashboard_statistics"),
    url(r"^statistics/get/$", "get_statistics", name="issue_statistic"),
)

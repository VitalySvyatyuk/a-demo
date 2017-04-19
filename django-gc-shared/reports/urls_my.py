# -*- coding: utf-8 -*-

from django.conf.urls import *


urlpatterns = patterns("reports.views",
    url("^view_groups/$", "view_groups",
        name="reports_view_groups"
    ),
    url("^$", "report_list",
        name="reports_report_list"
    ),
    url("^result/(?P<report_id>\d+)/$", "view_report",
        name="reports_view_report"),
    url("^excel_export/$", "marketing_inout_report",
        name="reports_marketing_inout_report"),
)

# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns("shared.views",
    url(r"^video_count/$", "video_view_count",
        name="video_view_count"),
    url(r"^easy_comments/$", "easy_comments_update",
        name="easy_comments_update"),
)

# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns("geobase.views",
    url(r"autocomplete/region/$", "autocomplete_region",
        name="geobase_autocomplete_region"),
    url(r"autocomplete/city/(?P<limit>\d+)/$", "autocomplete_city",
        name="geobase_autocomplete_city"),
)

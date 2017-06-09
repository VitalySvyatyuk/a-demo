# -*- coding: utf-8 -*-

from django.conf.urls import *

urlpatterns = patterns('contract_specs.views',
    # url(r'^contract_specs/$', 'symbols_for_instrument',
    #     name='contract_spec_index'),
    # url(r'^contract_specs/(?P<acc_type_raw>[\w_]+)(/(?P<spec_type_raw>[\w_]+))?/$', 'symbols_for_instrument',
    #     name='contract_spec_index'),z
    url(r'^specifications/$', "specifications",
        name="specifications"),
    url(r'^specifications/(?P<slug>[^/]+)/$', "specifications",
        name="specifications"),
    url(r'^margin_requirements/$', "margin_requirements",
        name="margin_requirements"),
    url(r'^margin_requirements/(?P<slug>[^/]+)/$', "margin_requirements",
        name="margin_requirements"),
    url(r'^specifications/details/(?P<pk>[^/]+)/$', "specification_details",
        name="specification_details"),
    url(r'^calculator/$', "calculator",
        name="trading_calculator"),

)

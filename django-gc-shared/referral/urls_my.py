# -*- coding: utf-8 -*-

from django.conf.urls import *


urlpatterns = patterns("referral.views",
    url(r'^certificate/partner_certificate.pdf$', 'partner_certificate_download',
        name='referral_partner_certificate_download'),
    url(r'^get_partner_certificate/$', 'partner_certificate',
        name='referral_partner_certificate'),
    url(r'^documents/$', 'partner_documents',
        name='referral_partner_documents'),
    url("^verify/$", "verify_partner",
        name="referral_verify_partner"),
    url(r'^clicks/$', 'referral_click_count',
        name='referral_click_count'),
    url(r'^delete_domain/$','delete_domain',name='delete_domain'),
    url(r"^add_domain/$",'add_domain',name='add_domain'),
)

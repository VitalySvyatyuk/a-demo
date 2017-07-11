# -*- coding: utf-8 -*-

from django.conf.urls import *
from shared.generic_views import TemplateView


urlpatterns = patterns(
    "project.views",
    url(r"^$", 'frontpage', name="frontpage"),
    url(r"^widget/$", TemplateView.as_view(
        template_name="marketing_site/pages/test.html"), name="about",),
    url(r"^about/$", TemplateView.as_view(
        template_name="marketing_site/pages/about.jade"), name="about",),
    url(r"^advantages/$", TemplateView.as_view(
        template_name="marketing_site/pages/advantages.jade"), name="advantages",),
    url(r"^contacts/$", TemplateView.as_view(
        template_name="marketing_site/pages/contacts.jade"), name="contacts",),
    url(r"^account-types/$", TemplateView.as_view(
        template_name="marketing_site/pages/account-types.jade"), name="account-types",),
    url(r"^inout/$", 'inout', name="inout",),
    url(r"^mt4/$", TemplateView.as_view(
        template_name="marketing_site/pages/mt4.jade"), name="mt4",),
    url(r"^partnership/$", "partnership", name="partnership",),
    url(r"^vip/$", TemplateView.as_view(
        template_name="marketing_site/pages/vip.jade"), name="vip",),
    url(r"^webinar-item/$", TemplateView.as_view(
        template_name="marketing_site/pages/webinar-item.jade"), name="webinar-item",),
    url(r"^comparison/$", TemplateView.as_view(
        template_name="marketing_site/pages/comparison.jade"), name="comparison",),
    url(r"^arumpro/$", TemplateView.as_view(
        template_name="marketing_site/pages/arumpro.jade"), name="arumpro",),
    url(r"^ecn/$", TemplateView.as_view(
        template_name="marketing_site/pages/ecn.jade"), name="ecn",),
    url(r"^innovation/$", TemplateView.as_view(
        template_name="marketing_site/pages/innovation.jade"), name="innovation",),
    url(r"^invest/$", TemplateView.as_view(
        template_name="marketing_site/pages/invest.jade"), name="invest",),
    url(r"^404/$", TemplateView.as_view(
        template_name="marketing_site/pages/404.jade"), name="404",),
    url(r"^subscribe/$", "send_subscribe_email", name="send_subscribe_email",),
)

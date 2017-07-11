# -*- coding: utf-8 -*-class ConsultPaymentIssue()
import os.path

from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from shared.generic_views import TemplateView

import issuetracker

admin.autodiscover()
issuetracker.autodiscover()


urlpatterns = patterns("",
    url(r"^admin/", include(admin.site.urls)),
    url(r"^accounts/", include("registration.urls_my")),
    url(r"^office/", include("payments.urls_my")),
    url(r"^office/accounts/", include("platforms.urls_my")),
    url(r"^profiles/", include("otp.urls_my")),
    url(r"^profiles/", include("profiles.urls_my")),
    url(r"^reports/", include("reports.urls_my")),
    url(r"^issues/", include("issuetracker.urls_my")),
    url(r"^issues_admin/", include("issuetracker.urls_admin")),
    # url(r"^captcha/(?P<code>[\da-f]{32})/$", "supercaptcha.draw"),
    url(r"^referral/", include("referral.urls_my")),
    url(r'^messages/', include('private_messages.urls_my')),
    url(r'^friend_recommed/', include('friend_recommend.urls_my')),
    url(r'^massmail/', include('massmail.urls_my')),
)

# Static files are usually served by web server, but the built-in
# is also okay for development setup.
if settings.DEBUG:
    urlpatterns += patterns("django.views.static",
        url(r"^%s/(?P<path>.*)$" % settings.STATIC_URL.strip('/'), "serve",
            {"document_root": settings.MEDIA_ROOT}),
        url(r"^img/(?P<path>.*)$", "serve",
            {"document_root": os.path.join(settings.MEDIA_ROOT, 'img')}),
    )

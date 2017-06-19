# -*- coding: utf-8 -*-
import os.path

from django.conf.urls import *
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.shortcuts import redirect

import issuetracker


admin.autodiscover()
admin.site.login = lambda req: redirect("auth_login")
issuetracker.autodiscover()

from shared.generic_views import TemplateView

from project.apirouter import APIRouter

urlpatterns = patterns("",
    url(r'', include("project.urls")),
    url(r'^api/', include(APIRouter.urls)),
    url(r'^cms/', include('uptrader_cms.urls')),
    url(r'^education/', include('education.urls')),
    url(r'^callback_request/', include('callback_request.urls')),
    url(r'^trading/', include('contract_specs.urls')),

    url(r'^social/complete/(?P<backend>[^/]+)/$', 'registration.views.complete_social_auth', name='complete'),
    url(r'^social/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^account/', 'project.views.app_my', name="account_app"),
    #Old named urls compatibility
    url(r'^account/profile/documents', 'project.views.app_my', name="profiles_upload_document"),
    #End old named urls compatibility
    url(r'^private_office/(?P<slug>[^/]+)/', 'project.views.private_offices', name="private_offices"),

    url(r'^mobile_account/', 'project.views.mobile_app_my', name="mobile_account_app"),

    url(r'^my/', include("sites.default.urls_my")),
       url(r"^geo/", include("geobase.urls")),
    url(r"^i18n/", include("i18n_extras.urls")),
    # url(r"^captcha/(?P<code>[\da-f]{32})/$", "supercaptcha.draw"),
    url(r"^rosetta/", include("rosetta.urls")),
    url(r'^ckeditor/', include('ckeditor.urls')),
    url(r'^ajax-lookups/', include('ajax_select.urls')),
    url(r'^massmail/', include('massmail.urls')),

    url(r"^jsi18n/$", "django.views.i18n.javascript_catalog",
        {"packages": ("payments", "transfers", "profiles", "templates", "otp"),
         'domain': 'djangojs'}, name="jsi18n"),
    # Separate translations for WebTrader because we shouldn't show GrandCapital strings in UpTrader
    url(r"^wti18n/$", "django.views.i18n.javascript_catalog",
        {"packages": ("webtrader"),
         'domain': 'djangojs'}, name="wti18n"),
    url(r'^shared/', include('shared.urls')),
    url("^templates/(?P<category>[\w_\.]+)/(?P<name>[\w_\.]+).html$", 'project.views.render_template'),

    # url(r'^account/', 'project.views.app_my', name="frontpage"),

    url(r"^crm/", include("crm.urls")),
    url(r"^gcrm/", include("gcrm.urls", namespace='gcrm')),
    url(r'^notification/', include('notification.urls', namespace="notification")),
)

# Static files are usually served by web server, but the built-in
# is also okay for development setup.
if settings.DEBUG:
    urlpatterns += patterns("django.views.static",
        url(r"^%s/(?P<path>.*)$" % settings.MEDIA_URL.strip('/'), "serve",
            {"document_root": settings.MEDIA_ROOT}),
    )
    urlpatterns += staticfiles_urlpatterns()

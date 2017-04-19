# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'education.views',

    url(r'^$', 'list_questions', name="education_frontpage"),
    url(r'^faq/$', 'list_questions', name="education_faq"),
    url(r'^glossary/$', 'list_terms', name="education_glossary"),
    url(r'^webinars/$', 'list_webinars', name="education_webinars"),

    url(r'^term/(?P<pk>[^/]+)/$', "term_details",
        name="term_details"),

    url(r'^webinars/(?P<slug>[^/]+)/$', "webinar_details",
        name="webinar_details"),
    url(r'^webinars/(?P<slug>[\w-]+)/registration/$',
        'webinar_registration',
        name='webinar_registration',),
)

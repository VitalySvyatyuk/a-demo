# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.conf.urls import *

from .views import app, render_template

urlpatterns = [
    url(r'^templates/(?P<name>[\w_\.]+).html$', render_template, name="render_template"),
    url(r'^', app, name="app"),
]

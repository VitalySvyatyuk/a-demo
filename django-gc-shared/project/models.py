# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division
from django.utils.translation import ugettext_lazy as _

# This is needed for
from django.contrib.auth.models import Group

GROUP_NAMES = (
    ('Portfolio management', _("Common question")),
    ('Dealing room', _("Technical question")),
    ('Back office', _("Financial question")),
    ('Partnership', _("Partnership department")),
)

# Monkeypatch auth.Group to have a method for name translation
# FIXME: is there a shorter and more django-way to do that?
Group.get_name_display = lambda self: dict(GROUP_NAMES).get(self.name)
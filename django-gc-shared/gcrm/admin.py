# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    raw_id_fields = ('user', 'manager')

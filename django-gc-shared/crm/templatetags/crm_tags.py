# -*- coding: utf-8 -*-

from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape

register = template.Library()


@register.simple_tag
def crm_show_phone(phone):
    if phone == u"+7 953 142 01 12":
        return u"+7 953 142 00 53"
    else:
        if not phone:
            return ""
        return mark_safe('<a href="skype:%s?call">%s</a>' % (u''.join(char for char in phone if char.isdigit() or char == u"+"),
                                                             escape(phone)))


@register.filter
def pretty_seconds(seconds):
    from crm.utils import seconds_to_string
    return seconds_to_string(seconds)

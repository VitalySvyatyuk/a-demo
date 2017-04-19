# -*- coding: utf-8 -*-

from collections import OrderedDict
from datetime import datetime
from dateutil.relativedelta import relativedelta

from django import template
from django.utils.html import escape
from django.utils.translation import override

register = template.Library()


@register.assignment_tag(takes_context=True)
def get_week_events(context, week):
    return context["calendar"].get_week_events(week)


@register.assignment_tag(takes_context=True)
def get_day_events(context, day):
    return context["calendar"].get_day_events(day)


@register.simple_tag
def get_day_name(week_day):
    from django.utils.dates import WEEKDAYS
    return WEEKDAYS[week_day]


@register.simple_tag
def get_month_name(month_num, lang=None, *args, **kwargs):
    from django.utils.dates import MONTHS
    if lang:
        with override(lang, deactivate=True):
            return unicode(MONTHS[month_num])
    return MONTHS[month_num]


@register.simple_tag
def calendar_querystring(month, year, category=None, direction=None, tz=None):

    d = datetime(year, month, 1)

    if direction == "fw":
        d = d + relativedelta(months=1)
    elif direction == "bw":
        d = d + relativedelta(months=-1)

    res = OrderedDict()
    res["month"] = d.month
    res["year"] = d.year

    if category:
        res["category"] = escape(category)

    if tz:
        res["tz"] = escape(tz)

    return "&".join("%s=%s" % x for x in res.items())

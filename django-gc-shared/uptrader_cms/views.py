# coding: utf-8
import json
from datetime import timedelta, datetime

from annoying.decorators import render_to
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.html import strip_entities
from django.utils.translation import ugettext_lazy as _, get_language

from geobase.utils import get_local_time_tz
from uptrader_cms.forms import CalendarForm
from uptrader_cms.models import IndicatorEvent, CompanyNews, LegalDocument
from project.templatetags.app_tags import as_timestamp
from shared.forms import MinMaxDateForm


@render_to('uptrader_cms/object_list.html')
def object_list(request, model, field_name='event_date', items_per_page=20,
                grouper='month'):

    form = MinMaxDateForm(request.POST or request.GET or None)
    events = model.objects.order_by('-event_date').filter(language=get_language())
    if form.is_valid():
        events = form.save(events)
        # Commented out this, cause this is completely useless
        # grouper = form.get_grouper(grouper)

    context = {
        'form': form,
        'events': events,
        'model': model,
        'title': model._meta.verbose_name_plural,
        'field_name': field_name,
        'items_per_page': items_per_page,
        'grouper': grouper
    }

    return context


def get_calendar_data(request, weekly=True):
    qs = IndicatorEvent.objects.order_by("event_date")
    form = CalendarForm(request.GET or None)
    current_day = None

    if form.is_valid():
        if form.cleaned_data["country"]:
            qs = qs.filter(indicator__country=form.cleaned_data["country"])
        if form.cleaned_data["importance"]:
            qs = qs.filter(importance=form.cleaned_data["importance"])

        if form.cleaned_data["day"]:  # change to single day
            current_day = form.cleaned_data["day"]
            # current_week = form.cleaned_data["start_date"], form.cleaned_data["end_date"]
            # week_for_range is needed to include events of end_date in select
            # week_for_range = form.cleaned_data["start_date"], form.cleaned_data["end_date"] + timedelta(1)
            qs = qs.filter(event_date=current_day)

    if weekly:
        if current_day is None:
            today = datetime.now().date()
            current_week = (today, today + timedelta(days=7-today.weekday()))
            qs = qs.filter(event_date__range=current_week)
    else:
            qs = qs.filter(event_date__gt=datetime.now())

    nearest_events = (
        IndicatorEvent.objects.order_by("event_date")
                              .filter(event_date__gt=datetime.now())
    )
    delta_str = ""
    if nearest_events:
        nearest_event = nearest_events[0]
        delta = relativedelta(nearest_event.event_date, datetime.now())
        delta_str = "%02d:%02d:%02d" % (
            delta.days*24 + delta.hours, delta.minutes, delta.seconds
        )
        nearest_events = [
            {
                "event_date": as_timestamp(x.event_date),
                "country_code": x.indicator.country.code if x.indicator.country else None,
                "name": strip_entities(x.indicator.name),
            }
            for x in nearest_events
        ]
    else:
        nearest_event = []
        nearest_events = []

    tz, local_time, tz_name = get_local_time_tz(request)
    return {
        'events': qs,
        'form': form,
        'nearest_event': nearest_event,
        'nearest_events': json.dumps(nearest_events),
        'to_nearest_event': delta_str,
        'tz': tz,
        'local_time': local_time,
        'tz_name': tz_name,
    }


@render_to('uptrader_cms/analytics-calendar.html')
def economic_calendar(request):
    return get_calendar_data(request)


@render_to("uptrader_cms/company_news_list.jade")
def company_news(request):
    news_items = CompanyNews.objects.published().filter(language=get_language())
    paginator = Paginator(news_items, 10)

    page = request.GET.get('page')

    try:
        news_items = paginator.page(page or 1)
    except PageNotAnInteger:
        news_items = paginator.page(1)
    except EmptyPage:
        news_items = paginator.page(paginator.num_pages)

    context = {
        "object_list": news_items,
        "header": _("Company news")
    }

    return context


@render_to("marketing_site/pages/legal-info.jade")
def legal_documentation(request):
    return {
        "documents": LegalDocument.objects.filter(
            languages__contains=[request.LANGUAGE_CODE]).order_by('priority')
    }

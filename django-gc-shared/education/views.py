# -*- coding: utf-8 -*-

from collections import defaultdict
from json import dumps
from datetime import datetime

import pytz
from django.contrib.auth.decorators import login_required
from annoying.decorators import render_to
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect

from education.models import WebinarEvent, Webinar, WebinarRegistration
from education.webinars_calendar import WebinarsCalendar
from notification import models as notification
from faq.models import Question, Category


@render_to('education/education_webinars.jade')
def list_webinars(request):
    try:
        month = int(request.GET.get("month") or datetime.now().month)
        year = int(request.GET.get("year") or datetime.now().year)
    except ValueError:
        raise Http404()

    category = request.GET.get("category") or None
    tz = request.GET.get("tz")

    q = Q()
    if category and category != "all":
        q |= Q(webinar__category=category)

    events = (
        WebinarEvent.objects.filter(
            q,
            starts_at__month=month,
            starts_at__year=year,
            webinar__language=request.LANGUAGE_CODE).order_by("starts_at")
    )

    calendar = WebinarsCalendar(year, month, events, tz=tz or "Europe/Moscow")

    timezones = defaultdict(list)
    for tz_global, tz_local in [x.split('/', 1) for x in pytz.common_timezones if "/" in x]:
        timezones[tz_global].append(tz_local)

    return {
        "month": month,
        "year": year,
        "category": category,
        "webinars": Webinar.objects.filter(favorite=True).order_by("category"),
        # "events": events,
        "calendar": calendar,
        "timezones": dumps(timezones),
        "tz": tz,
    }


@render_to('education/webinar_details.jade')
def webinar_details(request, slug):
    event = get_object_or_404(WebinarEvent.objects.select_related('webinar'), slug=slug)
    return {
        "event": event,
        "next_webinars": WebinarEvent.objects.filter(
            starts_at__gte=datetime.now(),
            webinar__language=request.LANGUAGE_CODE
        ).exclude(pk=event.pk).order_by('starts_at')
    }


@login_required
def webinar_registration(request, slug):

    tutorial = get_object_or_404(WebinarEvent, slug=slug)
    regs = WebinarRegistration.objects.filter(user=request.user, tutorial=tutorial)

    if not regs.exists():
        reg = WebinarRegistration(user=request.user, tutorial=tutorial)
        reg.save()

        notification.send(
            [request.user.email],
            "webinar_registration",
            {"event": reg.tutorial})

    return redirect(reverse('account_app') + 'webinars')


@render_to('education/education_faq.jade')
def list_questions(request):
    return {
        "questions": Question.objects.filter(
            lang=request.LANGUAGE_CODE,
            categories__faq_version=Category.MAIN_FAQ,
            published=True
        ).prefetch_related('categories').order_by('-categories__priority')
    }


@render_to('education/education_glossary.jade')
def list_terms(request):
    return {
        "terms": Question.objects.filter(
            lang=request.LANGUAGE_CODE,
            categories__faq_version=Category.GLOSSARY,
            published=True)
    }


@render_to('education/term_details.jade')
def term_details(request, pk):
    term = get_object_or_404(Question, pk=pk)
    return {
        "term": term,
        "other_terms": Question.objects.filter(
            lang=request.LANGUAGE_CODE,
            published=True
        ).exclude(pk=term.pk).order_by('-priority')[:5]
    }

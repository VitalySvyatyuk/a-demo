# -*- coding: utf-8 -*-
from datetime import *

from annoying.decorators import render_to, ajax_request
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q, ObjectDoesNotExist, Count, Sum
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.utils import formats

from crm.models import PersonalManager, CustomerRelationship, UserDataViewQuotaExceeded
from crm.utils import CORS
from crm.utils import can_manager_access_user
from profiles.models import UserProfile
from telephony.models import CallDetailRecord, VoiceMailCDR


def manager_by_client_num(request, phone):
    if request.META['REMOTE_ADDR'] not in settings.TELEPHONY_ASTER_IPS:
        raise Http404()

    valid_up = UserProfile.objects \
        .similar_by_phone(phone) \
        .order_by('-id') \
        .first()

    if not valid_up or not valid_up.manager:
        return HttpResponse()
    try:
        return HttpResponse(valid_up.manager.crm_manager.sip_name)
    except ObjectDoesNotExist:
        return HttpResponse()


@CORS(
    "https://grandcapital.amocrm.ru",
    allow_credentials=True,
    headers=["Content-Type", "amotok", "accept", "origin", "*"],
    methods="GET")
@ajax_request
def records_by_user(request, uid):
    user = get_object_or_404(User, id=uid)
    return {'data': [{
        'id': cdr.pk,
        'call_date': formats.date_format(cdr.call_date, "DATETIME_FORMAT"),
        'source': cdr.source_str(),
        'dest': cdr.dest_str(),
        'duration': cdr.duration,
        'disposition': cdr.disposition,
        'record': cdr.get_record_path(),
    } for cdr in user.profile.phone_calls().order_by('-call_date')]}


@CORS(
    "https://grandcapital.amocrm.ru",
    allow_credentials=True,
    headers=["Content-Type", "amotok", "accept", "origin", "*"],
    methods="GET")
@ajax_request
def voicemail_records_by_user(request, uid):
    user = get_object_or_404(User, id=uid)
    qs = VoiceMailCDR.objects.filter(cdr__user_a=user).order_by('-call_date')
    return {'data': [{
        'id': vmcdr.pk,
        'call_date': formats.date_format(vmcdr.call_date, "DATETIME_FORMAT"),
        'source': vmcdr.cdr.source_str(),
        'record': vmcdr.get_record_path(),
    } for vmcdr in qs]}


@login_required
@ajax_request
def calls_ajax(request):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    data = {}
    qs = CallDetailRecord.objects.all()

    if request.GET.get('status', 'all') != 'all':
        if request.GET.get('status') == 'answered':
            qs = qs.filter(disposition='ANSWERED')
        else:
            qs = qs.exclude(disposition='ANSWERED')

    if request.GET.get('search'):
        s = request.GET.get('search')
        q = Q()
        for str in s.split():
            str = str.strip()
            if str:
                q = (q | Q(user_a__username__icontains=str) |
                     Q(user_a__email__icontains=str) |
                     Q(user_b__username__icontains=str) |
                     Q(user_b__email__icontains=str) |
                     Q(number_a__icontains=str) |
                     Q(number_b__icontains=str) |
                     Q(name_a__icontains=str) |
                     Q(name_b__icontains=str))
        qs = qs.filter(q)

    lowest_call_date = datetime(
        year=int(request.GET.get('year', 1)),
        month=int(request.GET.get('month', 1)),
        day=int(request.GET.get('day', 1)),
    )
    highest_call_date = None

    datestate = request.GET.get('datestate', 'none')
    if datestate == 'none':
        data['datenumbers'] = lambda qs: [dt.year for dt in qs.dates('call_date', 'year', order='DESC')]
    elif datestate == 'year':
        highest_call_date = lowest_call_date + relativedelta(years=+1)
        data['datenumbers'] = lambda qs: [dt.month for dt in qs.dates('call_date', 'month', order='DESC')]
    elif datestate == 'month':
        highest_call_date = lowest_call_date + relativedelta(months=+1)
        data['datenumbers'] = lambda qs: [dt.day for dt in qs.dates('call_date', 'day', order='DESC')]
    elif datestate == 'day':
        highest_call_date = lowest_call_date + relativedelta(days=+1)
        data['datenumbers'] = lambda qs: []

    qs = qs.filter(call_date__gte=lowest_call_date)
    if highest_call_date:
        qs = qs.filter(call_date__lt=highest_call_date)
    data['datenumbers'] = data['datenumbers'](qs)

    manager = request.user.crm_manager
    if manager.can_see_all_calls:
        allowed_managers = PersonalManager.objects.filter(user__is_active=True)
    else:
        allowed_managers = []
        #add self
        if manager.sip_name:
            allowed_managers.append(manager)

        #if manager is head, add managers of office into allowed
        if manager.is_office_supermanager:
            allowed_managers.extend(PersonalManager.objects.filter(office=manager.office, user__is_active=True))

        sip_names = [pm.sip_name for pm in allowed_managers if pm.sip_name]
        qs = qs.filter(Q(name_a__in=sip_names) | Q(name_b__in=sip_names))

    #calculate stats
    stats = dict()
    all_managers_sip = [pm.sip_name for pm in allowed_managers if pm.sip_name]
    stat_a = qs.filter(name_a__in=all_managers_sip).order_by('user_a')
    stat_a = stat_a.values('name_a').annotate(s=Sum('duration'))
    for stat in stat_a:
        stats[stat['name_a']] = stat['s']

    stat_b = qs.filter(name_b__in=all_managers_sip).order_by('user_b')
    stat_b = stat_b.values('name_b').annotate(s=Sum('duration'))
    for stat in stat_b:
        stats[stat['name_b']] = stats.get(stat['name_b'], 0) + stat['s']

    #finalize, add printable name for json
    stats = sorted([{
        'name': sip_name,
        'duration': duration
    } for sip_name, duration in stats.iteritems()], key=lambda x: x['duration'], reverse=True)

    #graph info
    graphqs = qs.extra({
        'call_date_month': 'extract(month from call_date)',
        'call_date_year': 'extract(year from call_date)',
        'call_date_week': 'extract(week from call_date)',
        'call_date_day': 'extract(day from call_date)',
        'call_date_hour': 'extract(hour from call_date)'
    })
    if datestate in ['none', 'year']:
        graphqs_a = (graphqs.order_by('name_a')
                            .filter(name_a__in=all_managers_sip)
                            .values('name_a', 'call_date_year', 'call_date_month', 'call_date_week')
                            .annotate(duration=Sum('duration'), count=Count('id')))
        graphqs_b = (graphqs.order_by('name_b')
                            .filter(name_b__in=all_managers_sip)
                            .values('name_b', 'call_date_year', 'call_date_month', 'call_date_week')
                            .annotate(duration=Sum('duration'), count=Count('id')))
    elif datestate == 'month':
        graphqs_a = (graphqs.order_by('name_a')
                            .filter(name_a__in=all_managers_sip)
                            .values('name_a', 'call_date_year', 'call_date_month', 'call_date_day')
                            .annotate(duration=Sum('duration'), count=Count('id')))
        graphqs_b = (graphqs.order_by('name_b')
                            .filter(name_b__in=all_managers_sip)
                            .values('name_b', 'call_date_year', 'call_date_month', 'call_date_day')
                            .annotate(duration=Sum('duration'), count=Count('id')))
    elif datestate == 'day':
        graphqs_a = (graphqs.order_by('name_a')
                            .filter(name_a__in=all_managers_sip)
                            .values('name_a', 'call_date_year', 'call_date_month', 'call_date_day', 'call_date_hour')
                            .annotate(duration=Sum('duration'), count=Count('id')))
        graphqs_b = (graphqs.order_by('name_b')
                            .filter(name_b__in=all_managers_sip)
                            .values('name_b', 'call_date_year', 'call_date_month', 'call_date_day', 'call_date_hour')
                            .annotate(duration=Sum('duration'), count=Count('id')))

    graph_data = dict()
    for graphqs, name_field in [(graphqs_a, 'name_a'), (graphqs_b, 'name_b')]:
        for stat in graphqs:
            if datestate in ['none', 'year']:
                year = int(stat['call_date_year'])
                week = int(stat['call_date_week'])

                d = datetime(year, 1, 4)  # The Jan 4th must be in week 1  according to ISO
                dt = d + timedelta(weeks=(week-1), days=-d.weekday())
            else:
                dt = datetime(
                    int(stat['call_date_year']),
                    int(stat['call_date_month']),
                    int(stat.get('call_date_day', 1)),
                    int(stat.get('call_date_hour', 1)))
            graph_data.setdefault(
                stat[name_field], dict()
            ).setdefault(dt, {
                'duration': 0,
                'count': 0,
            })

            gd = graph_data[stat[name_field]][dt]
            gd['duration'] += stat['duration']
            gd['count'] += stat['count']

    #postprocess, since json encoder does not support datetime object as key
    for name, gd in graph_data.iteritems():
        graph_data[name] = sorted((date, stat) for date, stat in gd.iteritems())

    #order and render
    qs = qs.order_by('-call_date', '-id')
    pages = Paginator(qs, 20)
    try:
        current_page = int(request.GET.get('page', 1))
    except ValueError:
        current_page = 1

    if current_page > pages.num_pages:
        current_page = 1
    page = pages.page(current_page)

    data.update({
        'year': lowest_call_date.year,
        'month': lowest_call_date.month,
        'day': lowest_call_date.day,
        'datestate': datestate,

        'total': pages.count,
        'num_pages': pages.num_pages,
        'page': current_page,
        'stats': stats,
        'graph_data': graph_data,
        'data': [{
            'id': o.pk,
            'call_date': o.call_date.isoformat() if o.call_date else '-',
            'src': o.source_str(False),
            'src_crm_link': o.user_a.profile.get_amo().get_url() if o.user_a else '',
            'dst': o.dest_str(False),
            'dst_crm_link': o.user_b.profile.get_amo().get_url() if o.user_b else '',
            'duration': o.duration,
            'disposition': o.disposition,
            'record': o.get_record_path(),
            'url': reverse('telephony_call', kwargs={'external_id': o.external_cdr_id, 'call_id': o.pk}),
        } for o in page.object_list]
    })
    return data


@login_required
@render_to("call.html")
def call(request, external_id, call_id):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    cdr = CallDetailRecord.objects.get(id=call_id, external_cdr_id=external_id)
    return {
        'cdr': cdr,
    }


@login_required
@ajax_request
def calls_by_user_ajax(request, user_id):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    elif not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        return HttpResponseForbidden(u'Доступ с данного IP ограничен')

    user = get_object_or_404(User, id=user_id)

    #check access
    if not can_manager_access_user(request.user, user):
        return HttpResponseForbidden(u'Доступ к данному клиенту ограничен')

    customer, c = CustomerRelationship.objects.get_or_create(grand_user=user)
    try:
        customer.record_access(request.user, request)
    except UserDataViewQuotaExceeded:
        return HttpResponseForbidden(u'Лимит просмотра исчерпан, попробуйте позже')

    return [{
        'id': cdr.pk,
        'call_date': cdr.call_date,
        'source': cdr.source_str(),
        'dest': cdr.dest_str(),
        'duration': cdr.duration,
        'disposition': cdr.disposition,
        'record': cdr.get_record_path(),
    } for cdr in user.profile.phone_calls().order_by('-call_date')]


@login_required
@ajax_request
def vmcalls_by_user_ajax(request, user_id):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    elif not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        return HttpResponseForbidden(u'Доступ с данного IP ограничен')

    user = get_object_or_404(User, id=user_id)

    #check access
    if not can_manager_access_user(request.user, user):
        return HttpResponseForbidden(u'Доступ к данному клиенту ограничен')

    customer, c = CustomerRelationship.objects.get_or_create(grand_user=user)
    try:
        customer.record_access(request.user, request)
    except UserDataViewQuotaExceeded:
        return HttpResponseForbidden(u'Лимит просмотра исчерпан, попробуйте позже')

    qs = VoiceMailCDR.objects.filter(cdr__user_a=user).order_by('-call_date')
    return [{
        'id': vmcdr.pk,
        'call_date': vmcdr.call_date,
        'source': vmcdr.cdr.source_str(),
        'duration': vmcdr.cdr.duration,
        'record': vmcdr.get_record_path(),
    } for vmcdr in qs]

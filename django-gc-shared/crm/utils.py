# -*- coding: utf-8 -*-

from datetime import datetime, timedelta, date, time
from functools import wraps

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404

from crm.models import PersonalManager, CustomerRelationship, UserDataViewQuotaExceeded
from reports.models import AccountGroup

Q_or = lambda q, q2: q | q2 if q else q2
Q_and = lambda q, q2: q & q2 if q else q2


def check_permissions_log_access(request, user_id):
    if not PersonalManager.objects.filter(user=request.user).exists():
        raise Http404()
    elif not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        return None, HttpResponseForbidden(u'Доступ с данного IP ограничен')

    user = get_object_or_404(User, pk=user_id)

    # check access
    if not can_manager_access_user(request.user, user):
        return None, HttpResponseForbidden(u'Доступ к данному клиенту ограничен')

    customer, c = CustomerRelationship.objects.get_or_create(grand_user=user)
    try:
        customer.record_access(request.user, request)
    except UserDataViewQuotaExceeded:
        return None, HttpResponseForbidden(u'Лимит просмотра исчерпан, попробуйте позже')
    return user, None


def can_manager_access_user(manager, user):
    if not manager.is_active:
        return False
    if manager.is_superuser or manager.has_perm('crm.view_all_clients') or manager.crm_manager.is_head_supermanager:
        return True
    profile = user.profile
    if profile.manager == manager or profile.ib_manager == manager:
        return True
    if user.accounts.real_ib().exists() and manager.crm_manager.works_with_ib:
        return True
    if manager.crm_manager.is_office_supermanager and profile.manager and manager.crm_manager.office == profile.manager.crm_manager.office:
        return True
    if profile.country and profile.country.name_ru in manager.crm_manager.country_state_names:
        return True
    if profile.state and profile.state.name_ru in manager.crm_manager.country_state_names:
        return True
    return False


def by_last_assigned(managers):
    if not managers:
        return None

    manager = min(list(managers), key=lambda x: x.last_assigned)
    manager.last_assigned = datetime.now()
    manager.save()
    return manager


def get_all_offices_agent_codes():
    # from crm.models import RegionalOffice
    # ag = AccountGroup.objects.get(pk=3)
    # ids = set(map(int, ag.account_mt4_ids))
    # offices_codes_str = ','.join(RegionalOffice.objects.values_list('agent_codes', flat=True))
    # ids.update([
    #     int(pk)
    #     for pk in offices_codes_str.split(',')
    #     if pk])
    return []


def is_office_code(agent_code):
    if int(agent_code) in get_all_offices_agent_codes():
        return True
    return False


def is_regional_office_client(profile):
    return profile.manager and profile.manager.crm_manager.office and profile.manager.crm_manager.office.is_our


def is_spb_school_client(profile):
    """
    Is not intended to use widely
    """
    school_manager = PersonalManager.objects.get(ib_account=10044)
    return profile.manager == school_manager.user


def CORS(origin, allow_credentials=False, headers=['*'], methods="GET"):
    def decorator(func):
        @wraps(func)
        def inner_decorator(request, *args, **kwargs):
            response = func(request, *args, **kwargs)
            response['Access-Control-Allow-Methods'] = methods
            response['Access-Control-Allow-Credentials'] = "true" if allow_credentials else "false"
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Headers'] = ", ".join(headers)
            return response
        return inner_decorator
    return decorator


def calculate_finish_time(assignee, at=None, force_time=None, now=None):
    """
    `at` -
        None - today, any time
        timedelta - today + delta
        date - date, any time
        time - today, time
    `force_time` - user in conjuction with `at` if it is timedelta
    """
    if not now:
        now = datetime.now()

    now_any_time = now.replace(
        hour=23,
        minute=59,
        second=59,
    )

    if not at:
        at = now_any_time

    elif isinstance(at, timedelta):
        at += now

    elif isinstance(at, date):
        at = datetime.combine(
            at,
            time(23, 59, 59)
        )
    elif isinstance(at, time):
        at = now.replace(
            hour=at.hour,
            minute=at.minute,
            second=at.second
        )

    if force_time:
        at = at.replace(
            hour=force_time.hour,
            minute=force_time.minute,
            second=force_time.second
        )

    any_time = ((at.hour, at.minute, at.second) == (23, 59, 59))
    is_today = ((at.year, at.month, at.day) == (now.year, now.month, now.day))

    # if task is planned for today, but we cannot complete it now, increase day
    if is_today and now.hour >= assignee.crm_manager.worktime_end.hour:
        at += timedelta(days=1)
        at = at.replace(hour=23, minute=59, second=59)

    # if task is set not for any time and manager cannot complete it in time
    # set it on next day to complete during all day
    elif not any_time and at.hour >= assignee.crm_manager.worktime_end.hour:
        at += timedelta(days=1)
        at = at.replace(hour=23, minute=59, second=59)

    # if task is set before manager worktime, set it to any time
    elif at.hour < assignee.crm_manager.worktime_start.hour:
        at = at.replace(hour=23, minute=59, second=59)

    # caturday? move it to monday
    if at.weekday() == 5:
        at += timedelta(2)
        at = at.replace(hour=23, minute=59, second=59)
    # sunday? move it to monday
    elif at.weekday() == 6:
        at += timedelta(1)
        at = at.replace(hour=23, minute=59, second=59)
    return at


def amo_sync_contact(amo, contact):
    from django.utils import translation

    translation.activate('ru')

    r = contact.get_amo_json(amo)
    result = amo.contacts_set([r])
    assert contact.oid or result
    is_new = contact.is_new
    if result:
        contact.oid = result.values()[0]
    contact.synced_at = datetime.now()
    contact.sync_at = None
    contact.save()
    contact.post_sync(is_new, amo)


def amo_sync_task(amo, task):
    result = amo.contact_tasks_set([
        task.get_amo_json(amo)
    ])
    assert task.oid or result
    if result:
        task.oid = result.values()[0]
    task.synced_at = datetime.now()
    task.sync_at = None
    task.save()


def prev_workday_since(today=None):
    today = today or date.today()
    if today.weekday() == 0:
        result = today - timedelta(3)
    elif today.weekday() == 6:
        result = today - timedelta(2)
    else:
        result = today - timedelta(1)
    return result


def get_local_agent_codes(with_none=True):
    """
    This agent codes can be used to get "direct" UserProfiles
    WARNING!!! This will return None too, but it cannot be used
    with django in-lookup. Be sure to exlude None before filtering
    """
    return list(PersonalManager.objects.filter(
        Q(office__isnull=True)|Q(office__is_our=True),
        ib_account__isnull=False,
    ).values_list(
        'ib_account', flat=True
    )) + [
        # Old managers
        0,
        10000,
        10008,
        10018,
        10027,
        10032,
        10034,
        10050,
        10051,
        10053,
        10058,
        10059,
        10070,
        10071,
        29013,

    ] + [
        None,  # No agent code at all
    ] if with_none else []


def seconds_to_string(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return u'%dдней%dчас%dмин%dсек' % (days, hours, minutes, seconds)
    elif hours > 0:
        return u'%dчас%dмин%dсек' % (hours, minutes, seconds)
    elif minutes > 0:
        return u'%dмин%dсек' % (minutes, seconds)
    else:
        return '%dсек' % (seconds,)

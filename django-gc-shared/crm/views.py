# -*- coding: utf-8 -*-

from copy import copy
from datetime import datetime, timedelta
from functools import wraps
from operator import or_

import dateutil.parser
from annoying.decorators import render_to, ajax_request
from django.contrib.admin import ModelAdmin
from django.contrib.admin.views.main import ChangeList, PAGE_VAR
from django.contrib.auth.decorators import permission_required, user_passes_test, login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponseRedirect, Http404, HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import dateformat
from django.utils import formats
from django.utils.decorators import available_attrs
from django.utils.timezone import LocalTimezone
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from ipaddr import IPv4Address, IPv4Network
from lxml import etree
from sorl.thumbnail import get_thumbnail
from crm.forms import ReceptionCallForm, ManagerReassignForm
from crm.models import CustomerRelationship, CallInfo, CRMComment, PlannedCall, CRMAccess, PersonalManager,\
    LinkRequest, AccountDataView, BrocoUser, ReceptionCall, FinancialDepartmentCall, UserDataViewQuotaExceeded
from crm.models import ManagerReassignRequest, Notification
from crm.utils import CORS, can_manager_access_user, check_permissions_log_access
from currencies import currencies
from currencies.money import Money
from log.models import Logger, Events
from platforms.exceptions import PlatformError
from platforms.models import TradingAccount
from platforms.types import real_regex
from notification import models as notification
from payments.models import DepositRequest, WithdrawRequest
from profiles.models import UserProfile

PRIVATE_OFFICE_PREFIX = "http://localhost:8000/"

PER_PAGE_CHOICES = (10, 20, 50, 100, 150, 200)


class UserCRMAdmin(ModelAdmin):
    list_filter = ("grand_user__accounts__is_fully_withdrawn",)
    search_fields = ("grand_user__accounts__mt4_id", "grand_user__first_name", "grand_user__last_name",
                     "grand_user__profile__phone_mobile", "grand_user__email", "grand_user__profile__city",
                     "grand_user__profile__country__name")
    date_hierarchy = "planned_calls__date"

    def lookup_allowed(self, lookup, value):
        if "grand_user__accounts__creation_ts__" in lookup or \
           "calls__date__" in lookup:  # Alternative date hierarchies
            return True
        return super(UserCRMAdmin, self).lookup_allowed(lookup, value)


class BrocoUserCRMAdmin(UserCRMAdmin):
    list_filter = ("broco_user__accounts__group", )
    search_fields = ("broco_user__accounts__mt4_id", "broco_user__name", "broco_user__phone", "broco_user__email",
                     "broco_user__city", "broco_user__country")


class ChangeListWithParams(ChangeList):
    """ Supports any GET parameters.

    Parameters specified in preserved_params will be preserved when building
    new URLs

    Parameters specified in discarded_params will be deleted when building
    new URLs
    """
    def __init__(self, *args, **kwargs):
        request = args[0]
        preserved_params = kwargs.pop('preserved_params')
        discarded_params = kwargs.pop('discarded_params')
        self.preserved_params = preserved_params
        request.GET = request.GET.copy()
        for param in discarded_params:
            request.GET.pop(param, None)
        super(ChangeListWithParams, self).__init__(*args, **kwargs)

    def get_queryset(self, request):
        full_params = self.params.copy()
        for param in self.preserved_params:
            self.params.pop(param, None)
        result = super(ChangeListWithParams, self).get_queryset(request)
        self.params = full_params.copy()
        return result


def can_access_crm(view_func):
    def has_enough_rights(user):
        try:
            return user.is_authenticated() and user.crm_access
        except CRMAccess.DoesNotExist:
            return False

    @user_passes_test(has_enough_rights, login_url=PRIVATE_OFFICE_PREFIX+"accounts/login/")
    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request, *args, **kwargs):
        if u'*' in request.user.crm_access.allowed_ips:
            return view_func(request, *args, **kwargs)

        for ip_net in request.user.crm_access.allowed_ips:
            if IPv4Address(request.META['REMOTE_ADDR']) in IPv4Network(ip_net):
                return view_func(request, *args, **kwargs)

        return HttpResponseForbidden()
    return _wrapped_view


@can_access_crm
@ensure_csrf_cookie
@render_to("crm/main.html")
def frontpage(request, manager_username=None, agent_code=None, broco=False):
    access = request.user.crm_access

    if broco and agent_code is not None:
        return HttpResponseForbidden()

    if not access:
        return HttpResponseForbidden()

    per_page = int(request.GET.get('per_page', 20))
    demo_filter = request.GET.get('demo_filter', False)
    only_demo = False

    admin_settings = BrocoUserCRMAdmin if broco else UserCRMAdmin

    cl = ChangeListWithParams(
        request,
        model=CustomerRelationship,
        list_filter=admin_settings.list_filter,
        list_display=(),
        list_display_links=(),
        date_hierarchy=admin_settings.date_hierarchy,
        search_fields=admin_settings.search_fields,
        list_select_related=False,
        list_per_page=per_page,
        list_editable=(),
        model_admin=admin_settings(model=CustomerRelationship, admin_site=None),
        discarded_params=(),
        preserved_params=('per_page', 'demo_filter',),
        list_max_show_all=200
    )

    if broco:
        profile_path = main_path = "broco_user"
        cl.query_set = cl.query_set.filter(broco_user__isnull=False)
    else:
        profile_path = "grand_user__profile"
        main_path = "grand_user"
        cl.query_set = cl.query_set.filter(grand_user__isnull=False)

    accounts_list = []

    if access.regional_access and agent_code is None:
        only_demo = True  # Will show only demo
        queries = []
        for city_or_region in request.user.crm_access.cities_and_regions:
            if city_or_region:
                queries.append(cl.query_set.filter(Q(**{profile_path+"__state__name__icontains": city_or_region})|
                                                   Q(**{profile_path+"__city__icontains": city_or_region})))
        cl.query_set = reduce(or_, queries)

    if access.is_ib_partner:
        ib_accounts = request.user.crm_access.ib_accounts

    if agent_code is None and not (access.regional_access or access.is_staff):
        if ib_accounts:
            return HttpResponseRedirect(redirect_to=reverse("crm_frontpage_by_agent_code", args=(ib_accounts[0],)))
        else:
            return HttpResponseForbidden()

    if agent_code is not None:
        if not (access.is_ib_partner or access.is_staff) or \
                (access.is_ib_partner and int(agent_code) not in ib_accounts):
            return HttpResponseForbidden()

        # accounts_list = _get_account_list_for_ib(agent_code)
        accounts_list = []
        cl.query_set = cl.query_set.filter(grand_user__accounts__mt4_id__in=accounts_list)

    if manager_username is not None:
        manager = get_object_or_404(User, username=manager_username)
        if broco:
            cl.query_set = cl.query_set.filter(**{profile_path+"__manager": manager})
        else:
            cl.query_set = cl.query_set.filter(Q(**{profile_path+"__manager": manager}) |
                                               Q(**{profile_path+"__ib_manager": manager}))

    if demo_filter == "only_real":
        cl.query_set = cl.query_set.filter(grand_user__accounts___group__regex=real_regex())

    cl.query_set = cl.query_set.distinct()  # We don't need any duplicate rows

    # Prefetch user data; also triggers join of "auth_user" table to the query which we'll need later
    cl.query_set = cl.query_set.select_related(main_path)

    cl_for_next_call_date_hierarchy = copy(cl)
    cl_for_next_call_date_hierarchy.query_set =\
        cl_for_next_call_date_hierarchy.query_set.filter(Q(planned_calls__manager=request.user) |
                                                         Q(planned_calls__manager__isnull=True),
                                                         planned_calls__date__isnull=False)
    cl_for_account_creation_ts_date_hierarchy = copy(cl)
    cl_for_account_creation_ts_date_hierarchy.date_hierarchy = main_path + "__accounts__creation_ts"
    cl_for_account_creation_ts_date_hierarchy.query_set =\
        cl_for_account_creation_ts_date_hierarchy.query_set.filter(**{main_path+"__accounts__creation_ts__isnull": False})
    cl_for_call_date_hierarchy = copy(cl)
    cl_for_call_date_hierarchy.date_hierarchy = "calls__date"

    if only_demo:
        cl.query_set = cl.query_set.extra(
            where=[
                """NOT EXISTS(SELECT mt4_mt4account.creation_ts FROM mt4_mt4account WHERE user_id = auth_user.pk """
                """AND "platforms_tradingaccount"."group_name" ~* '%s')""" % real_regex()
            ]
        )

    cl.get_results(request)
    users_paginator = cl.paginator

    page = int(request.GET.get(PAGE_VAR, 0))  # Page indices produced by {% pagination %}
    #                                           somehow start with 0, and I'm too lazy to debug it
    users = users_paginator.page(page+1).object_list

    managers_list = User.objects.filter(pk__in=UserProfile.objects.filter(manager__isnull=False).distinct().
                                        values_list('manager', flat=True)).order_by('first_name')

    result = {'user_crms': users,
              'ADMIN_PREFIX': PRIVATE_OFFICE_PREFIX,
              'cl': cl,
              'cl_for_next_call_date_hierarchy': cl_for_next_call_date_hierarchy,
              'cl_for_account_creation_ts_date_hierarchy': cl_for_account_creation_ts_date_hierarchy,
              'per_page_links': ((cl.get_query_string({'per_page': per_page_choice}), per_page_choice)
                                 for per_page_choice in PER_PAGE_CHOICES),
              'demo_filter_links': ((cl.get_query_string({'demo_filter': 'only_real'}), u"Только реальные"),
                                    (cl.get_query_string({'demo_filter': 'all'}), u"Все")),
              'no_demo': demo_filter == "only_real",
              'managers': managers_list,
              'cl_for_call_date_hierarchy': cl_for_call_date_hierarchy,
              'accounts_list': accounts_list,
              'is_superuser': request.user.is_superuser,
              'is_reception': request.user.crm_access.reception_access,
              'is_staff': request.user.crm_access.staff_access,
              'crm_access': request.user.crm_access,
              'view_manager': request.user.crm_access.view_manager,
              'view_agent_code': request.user.crm_access.view_agent_code,
              'is_broco': broco,
              }
    try:
        crm_manager = request.user.crm_manager
    except PersonalManager.DoesNotExist:
        pass
    else:
        cache_key = 'crm_free_customers_%d' % request.user.pk
        free_customers = cache.get(cache_key)
        if not free_customers:  # If we have absolutely no data, we will update it synchronously
            free_customers = update_free_customers_count(request.user, cache_key, async=False)
        free_real, free_demo, free_empty, free_ib, free_for_date = free_customers
        if datetime.now() - free_for_date > timedelta(minutes=10):
            # If data is just old, we will update it asynchronously
            update_free_customers_count.delay(request.user, cache_key)
        result.update({
            'free_for_date': free_for_date,
        })
        if crm_manager.works_with_ib:
            result.update({
                'ib_profiles_without_manager': free_ib,
            })
        else:
            result.update({
                'profiles_without_manager': free_real,
                'demo_profiles_without_manager': free_demo,
                'empty_profiles_without_manager': free_empty,
            })
    return result


@can_access_crm
@render_to("crm/main.html")
def broco_frontpage(request, manager_username=None, agent_code=None):
    is_staff = request.user.crm_access.staff_access
    regional_access = request.user.crm_access.regional_access_demo in (2, 3)
    if not (is_staff or regional_access):
        return HttpResponseForbidden()

    per_page = int(request.GET.get('per_page', 20))
    demo_filter = request.GET.get('demo_filter', False)

    cl = ChangeListWithParams(request, model=BrocoUser, list_filter=BrocoUserCRMAdmin.list_filter,
                              list_display=(), list_display_links=(), date_hierarchy=BrocoUserCRMAdmin.date_hierarchy,
                              search_fields=BrocoUserCRMAdmin.search_fields,
                              list_select_related=False, list_per_page=per_page,
                              list_editable=(), model_admin=BrocoUserCRMAdmin(model=BrocoUser, admin_site=None),
                              discarded_params=(), preserved_params=('per_page', 'demo_filter',),
                              list_max_show_all=200)
    accounts_list = []

    if manager_username is not None:
        manager = get_object_or_404(User, username=manager_username)
        cl.query_set = cl.query_set.filter(manager=manager)

    if regional_access:
        queries = []
        for city_or_region in request.user.crm_access.cities_and_regions:
            if city_or_region:
                queries.append(cl.query_set.filter(Q(state__icontains=city_or_region) |
                                                   Q(city__icontains=city_or_region), has_only_demo=True))
        cl.query_set = reduce(or_, queries)

    cl.query_set = cl.query_set.distinct()  # We don't need any duplicate rows

    cl_for_date_hierarchy = copy(cl)  # {% date_hierarchy %} template tag seems to have several problems with .extra()
    cl_for_account_creation_ts_date_hierarchy = copy(cl)
    cl_for_account_creation_ts_date_hierarchy.date_hierarchy = "accounts__creation_ts"
    cl_for_account_creation_ts_date_hierarchy.query_set = \
        cl_for_account_creation_ts_date_hierarchy.query_set.filter(accounts__creation_ts__isnull=False)
    cl_for_call_date_hierarchy = copy(cl)
    cl_for_call_date_hierarchy.date_hierarchy = "crm__calls__date"

    cl.query_set = cl.query_set.extra(select={'latest_account':
                                                  "SELECT crm_brocomt4account.creation_ts FROM crm_brocomt4account WHERE user_id = crm_brocouser.pk ORDER BY crm_brocomt4account.creation_ts DESC LIMIT 1"},
        order_by=['-latest_account'],
        where=["EXISTS(SELECT crm_brocomt4account.creation_ts FROM crm_brocomt4account WHERE user_id = crm_brocouser.pk)"])

    cl.get_results(request)
    users_paginator = cl.paginator

    page = int(request.GET.get(PAGE_VAR, 0)) # Page indices produced by {% pagination %} somehow start with 0,
    #                                          and I'm too lazy to debug it
    users = users_paginator.page(page+1).object_list
    user_crms = [CustomerRelationship.objects.select_related().get_or_create(broco_user=user)[0] for user in users]

    managers_list = User.objects.filter(pk__in=BrocoUser.objects.distinct().values_list('manager', flat=True))\
        .order_by('first_name')

    return {'user_crms': user_crms,
            'ADMIN_PREFIX': PRIVATE_OFFICE_PREFIX,
            'cl': cl,
            'cl_for_date_hierarchy': cl_for_date_hierarchy,
            'cl_for_account_creation_ts_date_hierarchy': cl_for_account_creation_ts_date_hierarchy,
            'per_page_links': ((cl.get_query_string({'per_page': per_page_choice}), per_page_choice)
                               for per_page_choice in PER_PAGE_CHOICES),
            'demo_filter_links': ((cl.get_query_string({'demo_filter': 'only_real'}), u"Только реальные"),
                                  (cl.get_query_string({'demo_filter': 'all'}), u"Все")),
            'no_demo': demo_filter == "only_real",
            'managers': managers_list,
            'view_manager': request.user.crm_access.view_manager,
            'view_agent_code': request.user.crm_access.view_agent_code,
            'is_staff': request.user.crm_access.staff_access,
            'cl_for_call_date_hierarchy': cl_for_call_date_hierarchy,
            'accounts_list': accounts_list,
            'is_superuser': request.user.is_superuser,
            'is_broco': True,
            }


def check_user_data_view_quota(user, ip=None):
    """
    Security: check if a user has exceeded his user data view quota
    """
    # we're superusers, we're so special!
    if user.is_superuser:
        return True

    def _security_notification(limit_type, email=True):
        Logger(user=user, event=Events.ACCOUNT_DATA_VIEW_EXCEEDED, ip=ip, params={
            'limit_type': limit_type,
        }).save()
        if email:
            subject = "%s has exceeded his %s CRM limit" % (user.email, limit_type)
            send_mail(subject=subject,
                      message="At %s %s from IP %s" % (datetime.now(), subject, ip),
                      from_email="info@arumcapital.eu",
                      recipient_list=('valexeev@grandcapital.net', 'kozlovsky@grandcapital.net'))

    view_count_last_ten_minutes = AccountDataView.objects.\
        filter(user=user, creation_ts__gte=datetime.now() - timedelta(minutes=10)).count()
    if user.crm_manager and user.crm_manager.daily_limit:
        daily_limit = user.crm_manager.daily_limit
    else:
        daily_limit = 200
    per_hour = daily_limit / 3.0
    per_ten = per_hour / 5.0

    if view_count_last_ten_minutes > per_ten:
        _security_notification('10 minute ({} views)'.format(per_hour), email=False)
        return False
    view_count_last_hour = AccountDataView.objects.filter(user=user,
                                                          creation_ts__gte=datetime.now() - timedelta(hours=1)).count()
    if view_count_last_hour > per_hour:
        _security_notification('1 hour ({} views)'.format(per_hour))
        return False
    view_count_last_day = AccountDataView.objects.filter(user=user,
                                                         creation_ts__gte=datetime.now().date()).count()

    if view_count_last_day > daily_limit:
        _security_notification('daily ({} views)'.format(daily_limit))
        return False

    return True


def _check_access(request, allow_reception=False):
    crm_id = request.POST.get('crm_id')
    try:
        crm = CustomerRelationship.objects.get(pk=crm_id)
    except CustomerRelationship.DoesNotExist:
        return

    if not check_user_data_view_quota(request.user, request.META.get('REMOTE_ADDR')):
        return

    try:
        crm_access = request.user.crm_access
    except CRMAccess.DoesNotExist:
        return
    if not crm_access.active:
        return
    if crm_access.staff_access or (allow_reception and crm_access.reception_access):
        return crm
    if crm_access.ib_access and not crm.is_broco():
        for account in crm.user.accounts.all():
            try:
                agent_code = account.get_info_db.agent_account
            except (InvalidAccount, APIError):
                continue
            if int(agent_code) in request.user.crm_access.ib_accounts:
                return crm
    if crm_access.regional_access_demo != 0 and crm.has_only_demo:
        if (crm.broco_user and crm_access.regional_access_demo in (2, 3)) or\
           (crm.grand_user and crm_access.regional_access_demo in (1, 3)):
                city = (crm.broco_user.city if crm.broco_user else crm.grand_user.profile.city)
                if not city:
                    return
                else:
                    city = city.lower()
                if crm.broco_user:
                    state = crm.broco_user.state
                elif crm.grand_user.profile.state:
                    state = crm.grand_user.profile.state.name.lower()
                else:
                    return
                for city_or_region in crm_access.cities_and_regions:
                    city_or_region = city_or_region.lower()
                    if city_or_region.lower() in state or\
                       city_or_region.lower() in city:
                        return crm


@can_access_crm
@require_POST
@ajax_request
def save_call(request, new_customer=False):
    crm = _check_access(request)
    if crm is None:
        return HttpResponseForbidden()
    comment = request.POST.get('comment')
    if new_customer:
        user_profile = crm.user.profile
        if (request.user.crm_manager.works_with_ib and user_profile.ib_manager is not None)\
                or (not request.user.crm_manager.works_with_ib and not
                    (user_profile.manager_auto_assigned and user_profile.manager is None)):
            return HttpResponseForbidden()
        status = request.POST.get('status')
        if status == "success":
            comment = u"<i>Успешный звонок новому клиенту:</i> " + comment
            user_profile = crm.user.profile
            if request.user.crm_manager.works_with_ib:
                user_profile.ib_manager = request.user
            else:
                user_profile.manager = request.user
            user_profile.save()
            next_call_date = request.POST.get("next_call_date")
            if next_call_date:
                planned_call = PlannedCall(customer=crm, manager=request.user)
                try:
                    planned_call.get_date_from_string(next_call_date)
                except ValueError:
                    pass
                else:
                    planned_call.save()
        elif status == "failure":
            comment = u"<i>Звонок новому клиенту не удался, причина:</i> " + comment
        elif status == "regional_office":
            comment = u"<i>Клиент из-под регионального офиса.</i> " + comment
            user_profile = crm.user.profile
            user_profile.manager = None
            user_profile.manager_auto_assigned = False
            user_profile.save()
        else:
            return HttpResponseForbidden()
    call = CallInfo(customer=crm, comment=comment, caller=request.user)
    call.save()

    return {'result': 'ok', 'call': (call.pk, call.get_date_string(), call.comment)}


@can_access_crm
@require_POST
@ajax_request
def save_link_request(request):
    crm = _check_access(request)
    if crm is None or crm.is_broco():
        return HttpResponseForbidden()
    try:
        mt4_acc = TradingAccount.objects.get(pk=int(request.POST.get('account_id')))
    except TradingAccount.DoesNotExist:
        return HttpResponseForbidden()
    if not crm.user.accounts.filter(pk=mt4_acc.pk):
        return HttpResponseForbidden()
    link_request = LinkRequest(customer=crm, comment=request.POST.get('comment'),
                               author=request.user, account=mt4_acc)
    link_request.save()

    return {'result': 'ok'}


@can_access_crm
@require_POST
@ajax_request
def save_planned_call(request):
    crm = _check_access(request)
    if crm is None:
        return HttpResponseForbidden()
    planned_call = PlannedCall(customer=crm, manager=request.user)
    try:
        planned_call.get_date_from_string(request.POST.get('new_date', ''))
    except ValueError:
        return HttpResponseForbidden()
    planned_call.save()

    return {'result': 'ok'}


@can_access_crm
@require_POST
@ajax_request
def save_comment(request):
    crm = _check_access(request)
    if crm is None:
        return HttpResponseForbidden()
    comment = CRMComment(customer=crm, text=request.POST.get('comment'), author=request.user)
    comment.save()

    return {'result': 'ok'}


@csrf_exempt
@can_access_crm
@require_POST
@ajax_request
def load_calls(request):
    crm = _check_access(request)
    if crm is None:
        return HttpResponseForbidden()
    calls = CallInfo.objects.filter(customer=crm).order_by('-date')
    return {'result': 'ok',
            'calls': [{'date': call.get_date_string(),
                       'comment': call.comment,
                       'caller': call.caller.get_full_name()} for call in calls]}


@csrf_exempt
@can_access_crm
@require_POST
@ajax_request
def load_account_info(request):
    acc_mt4_id = request.POST.get("mt4_id")
    try:
        account = TradingAccount.objects.filter(mt4_id=acc_mt4_id)[0]
    except IndexError:
        return HttpResponseForbidden()
    info = account.get_info('db')
    from structures.dict import to_dict
    info = to_dict(info)
    result = dict(((a, b) for a, b in info.iteritems() if not isinstance(b, datetime)))
    return result


@csrf_exempt
@can_access_crm
@require_POST
@render_to("crm/user_information_snippet.html")
def load_account_data(request, new_customer=False):
    if not new_customer:
        crm = _check_access(request, allow_reception=True)
        if crm is None:
            return HttpResponseForbidden()
    else:
        customer_type = request.POST.get('customer_type', None)
        if customer_type not in ("real", "demo", "empty", "ib", "failed_call"):
            raise Http404()
        if customer_type == "ib" and (not request.user.crm_manager or not request.user.crm_manager.works_with_ib):
            raise Http404()

        try:
            crm_access = request.user.crm_access
        except CRMAccess.DoesNotExist:
            return HttpResponseForbidden()
        if not (crm_access.active or crm_access.staff_access):
            return HttpResponseForbidden()
        try:
            user_profile = UserProfile.objects.crm_unassigned_customers(request.user, customer_type=customer_type)[0]
        except IndexError:
            raise Http404()
        crm = CustomerRelationship.objects.get_or_create(grand_user=user_profile.user)[0]
        crm.last_view_ts = datetime.now()
        crm.save()

    AccountDataView(customer=crm, user=request.user).save()
    return {'crm': crm, 'new_customer': new_customer}


@permission_required('crm.reception_call')
@render_to("crm/reception_call_form.html")
def reception_call_form(request):
    if request.method == "POST":
        form = ReceptionCallForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            if cd['switch_to'] == u"personal manager":
                if cd['account']:
                    try:
                        grand_user_account = TradingAccount.objects.get(mt4_id=cd['account'])
                        customer = CustomerRelationship.objects.get_or_create(grand_user=grand_user_account.user)
                        call_info = CallInfo.objects.create(caller=request.user, date=datetime.now(),
                                                            customer=customer[0])
                        call_info.save()
                    except TradingAccount.DoesNotExist:
                        pass
            rc = ReceptionCall(**cd)
            rc.save()
            return redirect("crm_reception_call_form")
        else:
            return {'form': form}
    else:
        return {'form': ReceptionCallForm()}


@csrf_exempt
@permission_required('crm.reception_call')
@require_POST
@ajax_request
def load_manager_data(request):
    acc_mt4_id = request.POST.get("account")
    # result = {'manager_assigned': False}
    # try:
    #     acc_mt4_id = int(acc_mt4_id)
    #     account = Mt4Account.objects.filter(mt4_id=acc_mt4_id)[0]
    # except (IndexError, ValueError):
    #     result.update({"show_account_error": True, "manager_name": None, 'internal_phone': None})
    #     return result
    # user_profile = User.objects.get(pk=account.user.pk).profile
    # if user_profile.manager:
    #     manager = user_profile.manager.crm_manager
    # else:
    #     manager = get_random_manager()
    #     user_profile.manager = manager.user
    #     user_profile.save()
    #     result['manager_assigned'] = True
    # manager = resolve_managers(manager)
    # result['manager_name'] = "%s %s" % (manager.user.first_name, manager.user.last_name)
    # result['internal_phone'] = manager.internal_phone
    # result['show_account_error'] = False
    # return result


@permission_required('crm.financial_dpt_call')
@render_to("crm/financial_dpt_form.html")
def financial_dpt_call_form(request):
    if request.method == "POST":
        account = request.POST.get('account')
        account = int(account) if (account and account.isdigit()) else None
        new_dpt_call = FinancialDepartmentCall(callee=request.user, name=request.POST.get('name'),
                                               description=request.POST.get('description'),
                                               account=account)
        new_dpt_call.save()
        return redirect("crm_financial_dpt_call_form")
    return {}


def crm_404(request):
    return HttpResponseNotFound("Not Found")


def get_investment_info(account):
    from pamm.models import PammMasterAccount, PammManagedAccount
    result = []
    if PammMasterAccount.objects.filter(account=account, is_active=True).exists():
        result.append(u"Управляющий")
    if PammManagedAccount.objects.filter(account=account, status__in=(1, 2)).exists():
        result.append(u"Инвестор")
    return u" ({})".format(u', '.join(result)) if result else u""


def uid_by_phone(request, phone):
    # simple ip protection
    good_ips = ['95.215.1.91', '127.0.0.1']
    if request.META['REMOTE_ADDR'] not in good_ips:
        raise Http404()

    # make sure phone starts with "+",
    # because every phone num in db
    # should start with "+"
    if not phone.startswith("+"):
        phone = "+" + phone
    ups = UserProfile.objects.filter(
        Q(phone_home=phone) |
        Q(phone_work=phone) |
        Q(phone_mobile=phone)
    ).order_by('-id')[:1]
    return HttpResponse() if not ups else HttpResponse('gcu{0}'.format(ups[0].user.pk))


@login_required
@render_to("crm/change_user_manager.haml")
def change_user_manager(request, user_id):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    user = get_object_or_404(User, pk=user_id)
    profile = user.profile

    req = ManagerReassignRequest(
        author=request.user,
        user=user,
        previous=profile.manager
    )
    form = ManagerReassignForm(request.POST or None, instance=req, request=request)

    if request.method == "POST" and form.is_valid():
        req = form.save()

        # instant change is possible only in the cases:
        # it is superuser
        # it is head manager(like S.Solovyov)
        # it is local reassignment(X office -> X office manager)
        #   and current user is supermanager in X office
        if (request.user.pk != 140743 and  # T. Volchetckiy. Sorry, I do not want to add yet another checkbox to admin
                (req.assign_to and (request.user.crm_manager.is_head_supermanager or request.user.is_superuser)) or
                (request.user.crm_manager.is_office_supermanager and req.is_local and req.assign_to and
                    req.assign_to.crm_manager.office == request.user.crm_manager.office) or not req.assign_to):
            req.accept(request.user, notify=True, completed_by_ip=request.META["REMOTE_ADDR"])

        # if this request wasn't instant, we should send notification about it to heads
        if not req.is_completed:
            supers = User.objects.filter(
                crm_manager__is_office_supermanager=True,
                crm_manager__office=None)
            notification.send(list(supers) + [req.author], 'crm_reassignrequest_new', {'obj': req})
    return {'profile': profile, 'form': form, 'obj': req}


@csrf_exempt
@require_POST
def snapengage_handler(request):
    # protection with agent_code
    assert 'snapabug' in request.META.get('HTTP_USER_AGENT')

    # for formatting, we need russan values, so...
    activate('ru')
    root = etree.XML(request.body)
    source_id = int(root.find('source_id').text)  # 2 for live chat, 1 for mail
    email = root.find('requested_by').text  # request author email
    created_at = dateutil.parser.parse(
        root.find('created_at').text
    ).astimezone(LocalTimezone())
    created_at_formatted = formats.date_format(created_at, "DATETIME_FORMAT")

    # lt's guess user...
    try:
        user = User.objects.get(email__iexact=email, profile__registered_from='')
    except User.DoesNotExist:
        user = None
    except User.MultipleObjectsReturned:
        raise User.MultipleObjectsReturned(u'Found two or more users with email {}'.format(email))

    # handle chats
    if source_id == 2:
        note_body = u"Онлайн-чат с клиентом от {created_at}\n\n" \
                    u"{log}\n\n" \
                    u"Дополнительная информация: {url}"
        logs = []
        transcripts = root.find('transcripts')
        if transcripts is not None:
            for transcript in transcripts:
                date = dateutil.parser.parse(
                    transcript.find('date').text
                ).astimezone(LocalTimezone())
                name = transcript.find('alias')
                if name is None:
                    name = transcript.find('id')
                logs.append(u"({time}) {name}: {message}".format(
                    name=name.text if name is not None else '',
                    time=formats.date_format(date, "TIME_FORMAT"),
                    message=transcript.find('message').text
                ))
            log = u'\n'.join(logs)
        else:
            log = u"n/a"

    # handle mails
    elif source_id == 1 and user:
        note_body = u"Клиент оставил сообщение через онлайн-чат от {created_at}\n\n" \
                    u"{log}\n\n" \
                    u"Дополнительная информация: {url}"
        log = root.find('description')
        log = log.text if log is not None else u"n/a"  # request first message

        if not user.profile.manager:
            user.profile.autoassign_manager(True)
        user.gcrm_contact.add_task(text=_(u"Process chat request received on {0}").format(created_at_formatted))

    # if user is available, create AmoNote
    if user:
        user.gcrm_contact.add_note(note_body.format(
            created_at=created_at_formatted,
            url=root.find('url').text,
            log=log
        ))
    return HttpResponse()


@login_required
@ajax_request
def retrieve_next_notification(request):
    notifications = Notification.objects.filter(is_sent=False, user=request.user)[:1]
    if not notifications:
        return {}

    notify = notifications[0]
    result = dict()
    result.update(notify.params)
    result.update({
        'text': notify.text,
        'type': notify.type,
        'type_display': notify.get_type_display(),
    })
    if notify.type == 'new_client':
        try:
            u = User.objects.get(id=notify.params['user_id'])
        except User.DoesNotExist:
            notify.delete()
            return retrieve_next_notification(request)
        result['crm_link'] = u.profile.get_amo().get_url()

    notify.is_sent = True
    notify.sent_at = datetime.now()
    notify.save()
    return result


@login_required
@render_to("crm/dashboard.html")
def dashboard(request):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    return {}


@login_required
@ajax_request
def search_ajax(request):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()

    # start query
    qs = UserProfile.objects.all()

    # fields to search
    if request.GET.get('method') == "ib":
        profile_fields = (
            "agent_code",
        )
    else:
        profile_fields = (
            "user__pk",
            "user__email",
            "user__first_name",
            "user__last_name",
            "user__accounts__mt4_id",
            "phone_home",
            "phone_work",
            "phone_mobile",
        )

    # ty django contrib/admin
    def construct_search(field_name):
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name
    # add lookups to fields
    profile_fields = map(construct_search, profile_fields)

    if request.GET.get('search'):
        # split query onto words, so we can search for "Mary 193"
        # to get Mary Quinn with purse 193453
        words = request.GET.get('search').strip().split(u" ")
        filter = Q()
        for word in words:
            sub_filter = Q()
            for field in profile_fields:
                sub_filter |= Q(**{field: word})
            filter &= sub_filter
        qs = qs.filter(filter)
    else:
        qs = qs.filter(Q(manager=request.user) | Q(ib_manager=request.user))

    def amo_link(profile):
        try:
            return profile.user.amo.get_url()
        except ObjectDoesNotExist:
            return ""

    def manager_to_str(user):
        if user == request.user:
            return u"Я"
        elif user:
            return unicode(user.profile)

    def user_fullname(profile):
        s = u""
        if profile.user.first_name:
            s += profile.user.first_name + u" "
        if profile.middle_name:
            s += profile.middle_name + u" "
        if profile.user.last_name:
            s += profile.user.last_name
        return s or unicode(profile)

    qs = qs.distinct().order_by('-user__date_joined')

    pages = Paginator(qs, 20)
    try:
        current_page = int(request.GET.get('page', 1))
    except ValueError:
        current_page = 1

    if current_page > pages.num_pages:
        current_page = 1
    page = pages.page(current_page)
    return {
        'total': pages.count,
        'num_pages': pages.num_pages,
        'page': current_page,

        'data': [{
            'id': obj.user.pk,
            'name': user_fullname(obj),
            'manager': manager_to_str(obj.manager) or '',
            'ib_manager': manager_to_str(obj.ib_manager) or '',
            'admin_url': reverse('admin:auth_user_change', args=(obj.user.pk,)),
            'profile_admin_url': reverse('admin:profiles_userprofile_change', args=(obj.user.profile.pk,)),
            'amo_url': amo_link(obj),
            'reassign_url': reverse('crm_change_user_manager', kwargs={'user_id': obj.user.pk}),
            'joined_at': formats.date_format(obj.user.date_joined, "DATETIME_FORMAT"),
        } for obj in page.object_list]
    }


@login_required
@ajax_request
def user_more_ajax(request):
    user, error = check_permissions_log_access(request, request.GET.get('user_id'))
    if error:
        return error

    return {
        'accounts': [{
            'id': acc.pk,
            'mt4_id': acc.mt4_id,
            'group': unicode(acc.group),
            'balance': unicode(acc.balance_money) if not(acc.is_deleted or acc.is_archived) else "0",
            'created_at': formats.date_format(acc.creation_ts, "DATETIME_FORMAT"),
            'is_deleted': acc.is_deleted,
            'is_archived': acc.is_archived,
        } for acc in user.accounts.all()]
    }


@login_required
@render_to("crm/user_page.html")
def user_page(request, user_id):
    user, error = check_permissions_log_access(request, user_id)
    if error:
        return error
    return {'user': user}


@login_required
@ajax_request
def logs_by_user_ajax(request, user_id):
    user, error = check_permissions_log_access(request, user_id)
    if error:
        return error

    return [{
        'id': log.pk,
        'ip': log.ip,
        'user': log.user.get_full_name() if log.user else '-',
        'at': log.at,
        'params': log.params,
        'event': log.event,
        'event_display': log.get_event_display(),
    } for log in user.profile.related_logs.order_by('-id')]


@login_required
@ajax_request
def user_deposit_requests_ajax(request, user_id):
    user, error = check_permissions_log_access(request, user_id)
    if error:
        return error
    drs = DepositRequest.objects.filter(account__in=user.accounts.all()).order_by('-creation_ts')
    return [{
        'id': dr.pk,
        'account': dr.account.mt4_id,
        'amount': unicode(dr.amount_money),
        'payment_system': unicode(dr.payment_system),
        'purse': dr.purse,
        'params': dr.params,
        'creation_ts': dr.creation_ts,
        'trade_id': dr.trade_id,
        'is_payed': dr.is_payed,
        'is_committed': dr.is_committed,
    } for dr in drs]


@login_required
@ajax_request
def user_withdraw_requests_ajax(request, user_id):
    user, error = check_permissions_log_access(request, user_id)
    if error:
        return error

    wrs = WithdrawRequest.objects.filter(account__in=user.accounts.all()).order_by('-creation_ts')
    return [{
        'id': wr.pk,
        'account': wr.account.mt4_id,
        'amount': unicode(wr.amount_money),
        'payment_system': unicode(wr.payment_system),
        'params': wr.params,
        'private_comment': wr.private_comment,
        'public_comment': wr.public_comment,
        'reason': wr.get_reason_display(),
        'group_id': wr.group.pk if wr.group else None,
        'group_link': wr.group.get_absolute_url() if wr.group else None,
        'closed_by': wr.closed_by.get_full_name() if wr.closed_by else None,
        'creation_ts': wr.creation_ts,
        'trade_id': wr.trade_id,
        'is_payed': wr.is_payed,
        'is_committed': wr.is_committed,
    } for wr in wrs]


@login_required
@ajax_request
def viewlogs_ajax(request):
    if not PersonalManager.objects.filter(user=request.user).exists():
        raise Http404()
    elif not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        return HttpResponseForbidden(u'Доступ с данного IP ограничен')

    qs = AccountDataView.objects.order_by('-creation_ts')

    if not (request.user.is_superuser or request.user.crm_manager.is_head_supermanager):
        qs = qs.filter(user=request.user)

    pages = Paginator(qs, 25)
    try:
        current_page = int(request.GET.get('page', 1))
    except ValueError:
        current_page = 1
    if current_page > pages.num_pages:
        current_page = 1
    page = pages.page(current_page)
    return {
        'total': pages.count,
        'num_pages': pages.num_pages,
        'page': current_page,

        'data': [{
            'id': adv.pk,
            'creation_ts': adv.creation_ts,
            'user_name': adv.user.get_full_name(),
            'customer_name': adv.customer.grand_user.get_full_name(),
            'customer_amo': adv.customer.grand_user.amo.get_url()
        } for adv in page.object_list]
    }


@login_required
@render_to("crm/survey.html")
def survey_page(request, user_id):
    user, error = check_permissions_log_access(request, user_id)
    if error:
        return error

    if request.user.crm_manager.office and not request.user.crm_manager.office.is_our:
        return HttpResponse()

    survey = UserSurvey.objects.filter(user_id=user_id).first()
    if request.POST:
        form = SurveyForm(request.POST, instance=survey, request=request)
        if form.is_valid():
            if survey:
                form.save()
            else:
                instance = form.save(commit=False)
                instance.user_id = user_id
                instance.save()
    else:
        form = SurveyForm(instance=survey, request=request)

    return {'form': form}

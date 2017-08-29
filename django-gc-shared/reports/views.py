# -*- coding: utf-8 -*-
import csv
import itertools
from datetime import date, timedelta

from annoying.decorators import render_to
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import StreamingHttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.utils.formats import get_format
from django.utils.translation import get_language
from django.utils.translation import ugettext as _
from django.views.static import serve

import reports
from models import SavedReport, AccountGroup
from platforms.models import TradingAccount
from payments.models import DepositRequest, BaseRequest
from reports.forms import ReportForm, MarketingInReportForm
from reports.utils import get_currency_conversion_date, has_perm_or_basicauth
from reports.tasks import generate_report


@login_required
@render_to("reports/report_list.html")
def report_list(request):
    # If we have an account_id provided via URI, using it as inital
    # value for the form.
    language = get_language()
    decimal_separator = get_format("DECIMAL_SEPARATOR", language, True)

    context = {
        "account": None,
        'user': request.user
    }

    if not request.user.accounts.real_ib().exists():
        return {
            "TEMPLATE": "reports/403.html"
        }

    excluded_for_user = set(AccountGroup.objects.excluded_for_user(request.user))

    if request.method == "POST":
        form = ReportForm(data=request.POST or None, **context)

        if form.is_valid():
            error_context = {
                "form": form,
                'DECIMAL_SEPARATOR': decimal_separator,
                'should_show_form': True,
                "reports": SavedReport.objects.filter(for_user=request.user).order_by('-creation_ts')
            }
            error_context.update(context)

            def error():
                messages.error(request, _("You aren't allowed to view reports of that type for account"))
                return error_context

            codename = form.cleaned_data.get("report_type")

            if not codename:
                return error()

            report = settings.REPORTS.get(codename)

            if not report:
                return error()

            account = None
            groups_to_include = None
            groups_to_exclude = None
            if report["type"] == reports.ACCOUNT_GROUP:
                groups_to_include = form.cleaned_data.get("account_group_include")
                # мы хотим проверить, есть ли указанные пользователем группы среди доступных ему
                # - если в форме указаны группы, то проверяем их вхождения
                # - если они в форме не были указаны (для групп включения это означает использовать все счета),
                #   то если юзер имеет разрешение reports.can_use_any_account - ему это разрешено, иначе нет.
                # так как set([None]) не является подмножеством ни пустого сета, ни реального,
                # то он покажет ошибку при проверке вхождений множеств.
                # set() является подмножеством любого сета и гарантированно пройдет проверку вхождения
                if groups_to_include:
                    groups_to_include = set(groups_to_include)
                else:
                    groups_to_include = set() if request.user.has_perm("reports.can_use_any_account") \
                        else set([None])

                groups_to_exclude = form.cleaned_data.get("account_group_exclude")
                groups_to_exclude = set(groups_to_exclude) if groups_to_exclude else set()

                available_inclusion_groups = set(AccountGroup.objects.for_user(request.user))
                available_exclusion_groups = available_inclusion_groups | excluded_for_user

                if (groups_to_include and not groups_to_include.issubset(available_inclusion_groups)) or \
                        (groups_to_exclude and not groups_to_exclude.issubset(available_exclusion_groups)):
                    return error()
            elif report["type"] == reports.GLOBAL:
                if not request.user.has_perm("reports.can_use_any_account"):
                    return error()
            elif report["type"] == reports.PRIVATE_OFFICE:
                pass  # No checks are required
            else:
                if not request.user.has_perm("reports.can_use_any_account"):
                    account = form.cleaned_data.get("account")
                    if account and account.user != request.user:
                        return error()
                else:
                    account = TradingAccount(mt4_id=int(request.POST.get("account")))

            if not request.user.has_perm("reports.can_generate_%s" % codename):
                return error()

            template = report.get('template_name') or "reports/%s.html" % codename

            report = SavedReport()
            report.for_user = request.user

            report.name = unicode(form) % settings.REPORTS[codename]["name"]
            report.save()

            form_data = {
                'account_group_include': groups_to_include or [],
                'account_group_exclude': groups_to_exclude or [],
                'account': account,
                'report_type': codename,
                'start': form.cleaned_data['start'],
                'end': form.cleaned_data['end'],
            }

            task = generate_report.delay(form_data, template, decimal_separator, report, language,
                                         request.user)
            report.celery_task_id = task.pk
            report.save()
            messages.success(request,
                             _("Your report order has been received and is now being processed. \
                      You will receive an email when the processing finishes."))
            return redirect("reports_report_list")
    else:
        today = date.today()
        form = ReportForm(initial={
            "start": today + relativedelta(day=1),
            "end": today + relativedelta(day=1, days=-1, months=1)
        }, **context)

    context["form"] = form
    context["reports"] = SavedReport.objects.filter(for_user=request.user).order_by('-creation_ts')
    context['DECIMAL_SEPARATOR'] = decimal_separator
    context['should_show_form'] = True
    context['excluded_for_user'] = excluded_for_user

    return context


@permission_required('reports.can_use_account_groups')
@render_to("reports/view_groups.html")
def view_groups(request):
    return {'account_groups': AccountGroup.objects.for_user(request.user),
            'should_show_form': True}


@login_required
def view_report(request, report_id):
    if request.user.is_superuser:
        report = get_object_or_404(SavedReport, pk=report_id)
    else:
        report = get_object_or_404(SavedReport, for_user=request.user, pk=report_id)
    return serve(request, path=report.filename, document_root=settings.SAVED_REPORTS_PATH)


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


@has_perm_or_basicauth('reports.can_use_excel')
@render_to("reports/base_report.html")
def marketing_inout_report(request):
    def generate_result_data(user, payment_request=None, account=None):
        result = []

        if account is not None:
            result.append(unicode(account.group))
            result.append(unicode(account.creation_ts.date()))
            result.append(unicode(account.pk))
        else:
            result.extend([''] * 3)

        if payment_request is not None:
            result.append(unicode(payment_request.creation_ts.date()))
            amount = payment_request.amount if isinstance(payment_request, DepositRequest) else -payment_request.amount
            result.append(unicode(amount))
            result.append(unicode(payment_request.currency))
            amount_usd = payment_request.amount_money.to('USD', for_date=get_currency_conversion_date(payment_request.creation_ts)).amount
            amount_usd = amount_usd if isinstance(payment_request, DepositRequest) else -amount_usd
            result.append(unicode(amount_usd))
            if amount < 0:
                result.extend(['', ''])
            result.append(unicode(amount))
            result.append(unicode(amount_usd))
            if amount >= 0:
                result.extend(['', ''])
            result.append(unicode(payment_request.payment_system))
        else:
            result.extend([''] * 9)

        result.append(unicode(user.pk))
        result.append(unicode(user.profile.country))
        result.append(unicode(getattr(user.profile.country, 'phone_code', '')))
        result.append(unicode(user.profile.state))
        result.append(unicode(user.profile.agent_code > 0))
        if hasattr(user, 'utm_analytics'):
            utm = user.utm_analytics
        else:
            utm = None
        if utm is not None:
            result.append(unicode(utm.agent_code_timestamp or ""))
        else:
            result.append("")
        result.append(unicode(user.date_joined.date()))
        if utm is not None:
            result.extend([utm.utm_source, utm.utm_medium, utm.utm_campaign,
                           unicode(utm.utm_timestamp or ""), utm.referrer,
                           unicode(utm.referrer_timestamp or "")])
        else:
            result.extend([''] * 6)
        if user.profile.manager:
            result.append(user.profile.manager.get_full_name())
        else:
            result.append("None")
        return result

    def deposit_data_generator(csv_writer, start, end):
        select_related = []
        for relation in ('depositrequest__', 'withdrawrequest__'):
            for relation2 in ('account', 'account__user', 'account__user__profile', 'account__user__profile__country',
                              'account__user__profile__state', 'account__user__profile__manager'):
                select_related.append(relation + relation2)

        for dr in BaseRequest.objects.prefetch_related('depositrequest', 'withdrawrequest').filter(
                is_committed=True,
                creation_ts__gte=start,
                creation_ts__lt=end + timedelta(days=1),
        ).select_related(*select_related).order_by('creation_ts'):
            dr = dr.as_leaf_class()
            if dr.account.user.is_staff:
                continue
            result = generate_result_data(user=dr.account.user, payment_request=dr, account=dr.account)
            yield csv_writer.writerow([item.encode('utf-8') for item in result])

    def registration_data_generator(csv_writer, start, end):
        for user in User.objects.filter(
                date_joined__gte=start,
                date_joined__lt=end + timedelta(days=1),
                is_staff=False,
        ).select_related('profile', 'profile__country', 'profile__state', 'profile__manager').order_by('date_joined'):
            result = generate_result_data(user=user)
            yield csv_writer.writerow([item.encode('utf-8') for item in result])

    def new_account_data_generator(csv_writer, start, end):
        for account in TradingAccount.objects.filter(
                creation_ts__gte=start,
                creation_ts__lt=end + timedelta(days=1),
                user__is_staff=False,
        ).select_related('user__profile', 'user__profile__country', 'user__profile__state',
                         'user__profile__manager').order_by('creation_ts'):
            result = generate_result_data(user=account.user, account=account)
            yield csv_writer.writerow([item.encode('utf-8') for item in result])

    if request.POST or "start" in request.GET:
        form = MarketingInReportForm(request.POST or request.GET)
        if form.is_valid():
            writer = csv.writer(Echo())
            response = StreamingHttpResponse(
                itertools.chain(
                    deposit_data_generator(writer, form.cleaned_data['start'], form.cleaned_data['end']),
                    registration_data_generator(writer, form.cleaned_data['start'], form.cleaned_data['end']),
                    new_account_data_generator(writer, form.cleaned_data['start'], form.cleaned_data['end']),
                ),
                content_type='text/csv'
            )
            response['Content-Disposition'] = 'attachment; filename="report.csv"'
            return response
    else:
        today = date.today()
        form = MarketingInReportForm(initial={
            "start": today + relativedelta(day=1),
            "end": today + relativedelta(day=1, days=-1, months=1)
        })
    return {
        'form': form,
        'should_show_form': True,
    }

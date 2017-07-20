# coding=utf-8
from datetime import date

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.formats import get_format
from django.utils.translation import get_language, ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import list_route
from rest_framework.response import Response

import reports
from platforms.models import TradingAccount, AbstractTrade
from reports.models import SavedReport, AccountGroup, SavedReportData
from reports.rest_serializers import SavedReportSerializer, ReportOrderSerializer
from reports.tasks import generate_report


class ReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SavedReportSerializer

    def get_queryset(self):
        return self.request.user.saved_reports.order_by('-creation_ts')

    @staticmethod
    def _generate_report_name(report_name, start, end, account, account_group_include, account_group_exclude,
                              report_type, as_user):
        result = u"(%s - %s)" % (unicode(start), unicode(end))

        if account:
            account = TradingAccount(mt4_id=account)

        if account:
            result += u" %s %s" % (_(u'for account'), account)
        if account_group_include:
            if account_group_exclude:
                result += " " + _(u'for account groups %(include)s without groups %(exclude)s') % {
                    'include': u", ".join(map(unicode, account_group_include)),
                    'exclude': u", ".join(map(unicode, account_group_exclude))
                }
            else:
                result += " " + _(u'for account group %s') % u", ".join(map(unicode, account_group_include))
        if as_user:
            result += u" от имени %s" % as_user.get_full_name()
        return report_name + ' ' + result

    @list_route()
    def get_current_result(self, request):
        dates_range = [date.today().replace(day=1), date.today()]
        ib_acc = request.user.accounts.real_ib().first()
        if not ib_acc or ib_acc.platform_type != 'mt4':
            return Response()
        from platforms.mt4 import RealTrade
        reward_this_month = RealTrade.objects.filter(login=ib_acc.mt4_id, cmd=6, symbol="IBPayment",
                                                     close_time__range=dates_range)\
                                    .aggregate(sum=Sum('profit'))['sum'] or 0
        if ib_acc:
            data = SavedReportData.objects.extra(
                where=["params::json ->> 'report_type' = 'all_partners_summary_2013' AND "
                       "(params::json ->> 'start')::date = %s AND "
                       "(params::json ->> 'end')::date = %s"],
                params=dates_range
            ).first()
            if data:
                for row in data.data['data']:
                    if row['login'] == ib_acc.mt4_id:
                        row['report_date'] = data.creation_ts
                        row['reward_this_month'] = reward_this_month
                        return Response(row)
        return Response()

    @list_route(methods=['post'], serializer_class=ReportOrderSerializer)
    def order_report(self, request):
        serializer = self.get_serializer(data=request.data)

        language = get_language()
        decimal_separator = get_format("DECIMAL_SEPARATOR", language, True)

        excluded_for_user = set(AccountGroup.objects.excluded_for_user(request.user))
        serializer.is_valid(raise_exception=True)

        #create report -_-
        codename = serializer.validated_data["report_type"]

        report = settings.REPORTS.get(codename)

        account = None
        groups_to_include = None
        groups_to_exclude = None
        as_user = request.user
        if report["type"] == reports.ACCOUNT_GROUP:
            groups_to_include = None
            if serializer.validated_data["account_group_include"]:
                groups_to_include = AccountGroup.objects.filter(
                    pk__in=serializer.validated_data["account_group_include"])
            # мы хотим проверить, есть ли указанные пользователем группы среди доступных ему
            # - если в форме указаны группы, то проверяем их вхождения
            # - если они в форме не были указаны (для групп включения это означает использовать все счета),
            # то если юзер имеет разрешение reports.can_use_any_account - ему это разрешено, иначе нет.
            # так как set([None]) не является подмножеством ни пустого сета, ни реального,
            # то он покажет ошибку при проверке вхождений множеств.
            # set() является подмножеством любого сета и гарантированно пройдет проверку вхождения
            if groups_to_include:
                groups_to_include = set(groups_to_include)
            else:
                groups_to_include = set() if request.user.has_perm("reports.can_use_any_account") \
                    else {None}

            groups_to_exclude = None
            if serializer.validated_data["account_group_exclude"]:
                groups_to_exclude = AccountGroup.objects.filter(
                    pk__in=serializer.validated_data["account_group_exclude"])
            groups_to_exclude = set(groups_to_exclude) if groups_to_exclude else set()

            available_inclusion_groups = set(AccountGroup.objects.for_user(request.user))
            available_exclusion_groups = available_inclusion_groups | excluded_for_user

            if (groups_to_include and not groups_to_include.issubset(available_inclusion_groups)) or \
                    (groups_to_exclude and not groups_to_exclude.issubset(available_exclusion_groups)):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif report["type"] == reports.GLOBAL:
            if not request.user.has_perm("reports.can_use_any_account"):
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif report["type"] == reports.PRIVATE_OFFICE:
            if request.user.has_perm("reports.can_use_any_user") and serializer.validated_data.get('user'):
                as_user = User.objects.get(pk=serializer.validated_data['user'])
        else:
            if not request.user.has_perm("reports.can_use_any_account"):
                account = TradingAccount.objects.filter(user=request.user, mt4_id=serializer.validated_data["account"]).first()

                if account and account not in request.user.accounts.real_ib():
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                account = TradingAccount(mt4_id=int(serializer.validated_data["account"]))

        if not request.user.has_perm("reports.can_generate_%s" % codename):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        template = report.get('template_name') or "reports/%s.html" % codename

        report = SavedReport()
        report.for_user = request.user

        form_data = {
            'account_group_include': groups_to_include or [],
            'account_group_exclude': groups_to_exclude or [],
            'account': account.mt4_id if account else None,
            'report_type': codename,
            'start': serializer.validated_data['start'],
            'end': serializer.validated_data['end'],
        }

        report.name = self._generate_report_name(settings.REPORTS[codename]["name"],
                                                 as_user=as_user if as_user != request.user else None,
                                                 **form_data)

        report.save()

        task = generate_report.delay(form_data, template, decimal_separator, report, language, as_user)
        report.celery_task_id = task.task_id
        report.save()
        return Response(SavedReportSerializer(report).data, status=status.HTTP_202_ACCEPTED)

# coding=utf-8

from datetime import datetime
from itertools import chain

import django_filters
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status, exceptions, filters
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from currencies.money import NoneMoney
from log.models import Event
from notification import models as notification
from otp.check import check_otp_drf
from otp.rest_permissions import IsOtpBinded
from platforms.models import AbstractTrade
from platforms.rest_permissions import AccountIsActive
from platforms.rest_serializers import (
    TradingAccountSerializer, LeverageSerializer,
    TradeSerializer, TradingAccountAgentSerializer,
    DemoDepositSerializer
)
from platforms.types import get_groups_regex


class TradingAccountViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TradingAccountSerializer
    permission_classes = (IsAuthenticated, IsOtpBinded,)
    paginator = None  # type: ignore

    @classmethod
    def get_base_queryset(cls, user, params=None, qs=None):
        if qs is None:
            qs = user.accounts.all()

        if params:
            allowed_methods = ['archived', 'trading', 'real_ib']
            for m in allowed_methods:
                if m in params:
                    qs = getattr(qs, m)()

            if 'group' in params:
                rx = get_groups_regex(params.getlist('group'))
                if rx:
                    qs = qs.filter(_group__iregex=rx)

            if 'archived' not in params:
                qs = qs.active()
        return qs

    def get_queryset(self):
        return self.get_base_queryset(self.request.user, self.request.query_params).order_by('-id')

    @list_route()
    def batch_mt4_data(self, request):
        ids = request.query_params.getlist('id', None)
        data = {}

        # first of, collect all accounts
        # we have access to
        accounts = self.get_queryset().filter(mt4_pk__in=ids)
        for acc in accounts:
            d = {}
            for attr in ('leverage', 'equity_money', 'balance_money', 'last_block_reason', 'referral_money'):
                try:
                    d[attr] = getattr(acc, attr, None)
                except:
                    d[attr] = None

            if not d['equity_money']: d['equity_money'] = NoneMoney()
            if not d['balance_money']: d['balance_money'] = NoneMoney()

            data[acc.mt4_id] = {
                'leverage': d['leverage'],
                'equity_amount': d['equity_money'].amount,
                'equity_display': unicode(d['equity_money']),
                'balance_display': unicode(d['balance_money']),
                'balance_amount': d['balance_money'].amount,
                'balance_currency': unicode(d['balance_money'].currency),
                'balance_usd_amount': d['balance_money'].to_USD().amount,
                'referral_usd_amount': d['referral_money'].amount,
                'rebate': None,
                'last_block_reason': d['last_block_reason']
            }
        return Response(data)

    @detail_route(methods=['post'], permission_classes=permission_classes + (AccountIsActive,))
    def recover_password(self, request, pk=None):
        account = self.get_object()
        if not account.is_demo:
            check_otp_drf('Account password recovery', self.request)
        Event.ACCOUNT_PASSWORD_RESTORED.log(account)

        new_password = account.change_password()
        login = account._login
        if not login:
            if account.group_name in ['demoARM', 'ARM_MT4_Live']:
                login = account.mt4_id
            elif account.group_name in ['realstandard_ss']:
                login = account.user.email
        notification_data = {"user_name": account.user.first_name,
                             "login": login, "account": account.mt4_id,
                             "password": new_password}

        if new_password:
            notification.send([account.user], "password_recovery", notification_data, no_django_message=True)
            return Response({
                'detail': _('Password recovered and sent on your email')
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'detail': 'Password recovery not supported'
            }, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(
        methods=['post'],
        permission_classes=permission_classes + (AccountIsActive,),
        serializer_class=LeverageSerializer)
    def change_leverage(self, request, pk=None):
        account = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not account.is_demo:
            check_otp_drf('Account leverege change', self.request)
        serializer.apply_leverage()

        return Response({
            'object': TradingAccountSerializer(account).data,
            'detail': _('Leverage successfully changed')
        }, status=status.HTTP_202_ACCEPTED)

    def leverage(self, request, pk=None):
        account = self.get_object()
        return Response({'leverage': account.leverage})

    def balance(self, request, pk=None):
        account = self.get_object()
        return Response({'balance': account.balance_money.amount})

    def equity(self, request, pk=None):
        account = self.get_object()
        return Response({'equity': account.equity_money.amount})

    @detail_route(methods=['post'])
    def restore(self, request, pk=None):
        account = self.get_base_queryset(self.request.user).archived().filter(pk=pk).first()
        if not account:
            raise exceptions.NotFound()

        if not account.is_archived:
            raise exceptions.MethodNotAllowed("Account isn't archived")

        if account.has_restore_issue:
            raise exceptions.MethodNotAllowed("Request already exists")

        from issuetracker.models import RestoreFromArchiveIssue
        issue = RestoreFromArchiveIssue(account=account)
        issue.save()
        return Response({
            'object': TradingAccountSerializer(account).data,
            'detail': _('Request to restore account has be created')
        }, status=status.HTTP_202_ACCEPTED)

    @detail_route(methods=['get'])
    def agents(self, request, pk=None):
        account = self.get_object()
        if account.is_archived:
            raise exceptions.MethodNotAllowed("Account archived")

        if not account.is_ib:
            raise exceptions.MethodNotAllowed("Only ib account has agents")

        agents = account.agent_clients

        data = TradingAccountAgentSerializer(agents, many=True).data
        return Response(data)

    @detail_route(
        methods=['post'],
        permission_classes=permission_classes + (AccountIsActive,),
        serializer_class=DemoDepositSerializer)
    def demo_deposit(self, request, pk=None):
        account = self.get_object()

        if not account.is_demo:
            raise exceptions.MethodNotAllowed("Invalid account type")

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        account.change_balance(
            amount=float(serializer.data['value']),
            comment='{demodeposit}',
            request_id=0,
            transaction_type=""
        )

        return Response({
            'object': TradingAccountSerializer(account).data,
            'detail': _('Balance successfully changed')
        }, status=status.HTTP_202_ACCEPTED)


def date_to_action(queryset, value):
    return queryset.filter(
        open_time__lte=datetime(value.year, value.month, value.day, 23, 59, 59)
    )


class TradeFilter(django_filters.FilterSet):
    date_from = django_filters.DateFilter(name='open_time', lookup_type='gte')
    date_to = django_filters.DateFilter(name='open_time', action=date_to_action)

    class Meta:
        model = AbstractTrade
        fields = ('date_from', 'date_to',)


class TradeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TradeSerializer
    permission_classes = (IsAuthenticated, IsOtpBinded,)

    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TradeFilter

    def get_queryset(self):
        account = self.request.user.accounts.active().filter(
            mt4_id=self.kwargs['account_id']
        ).first()
        if not account:
            raise exceptions.PermissionDenied

        if 'open' in self.request.query_params:
            qs = account.open_trades
        elif 'close' in self.request.query_params:
            qs = account.closed_trades
        elif 'deferred' in self.request.query_params:
            qs = account.deferred_trades
        else:
            qs = account.trades
        return qs.order_by('-ticket')

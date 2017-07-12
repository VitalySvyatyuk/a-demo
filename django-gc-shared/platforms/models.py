# -*- coding: utf-8 -*-
import math
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from model_manager import AdvancedManager

from currencies.currencies import get_by_group, Currency, USD
from currencies.money import Money, NoneMoney
from log.models import Event
from shared.models import CustomManagerMixin
from shared.utils import upload_to
from project.utils import queryset_like
from shared.werkzeug_utils import cached_property

import re, sys

from .types import (
    RealMicroAccountType,
    StandardAccountType,
    get_account_type,
    demo_regex,
    micro_regex,
    real_accounts_for_forex_regex)

TYPE_OF_AGREEMENT = (
    ('simple_with_documents', u"Простое подписание, документы отправлены через форму на сайте"),
    ('simple_no_documents', u"Простое подписание, документы уже в офисе"),
    ('oferta', u"Согласие с офертой"))

TYPE_OF_PLATFORM = (
    ('mt4', u"Meta Trader 4"),
    ('cfh', u"CFH"),
    ('strategy_store', u"Strategy Store")
)

import logging
log = logging.getLogger(__name__)


def normalize(account, value):
    if account.is_micro:
        return math.floor(value) / 100.0
    else:
        return value


class TradingAccountQueryset(models.query.QuerySet):
    def alive(self):
        return self.filter(is_deleted=False, is_archived=False)

    def active(self):
        return self.filter(is_deleted=False)

    def archived(self):
        return self.filter(is_deleted=True, is_archived=True)

        ###############################################################################
        ################# Functions to get certain type accounts  ######################
        ###############################################################################

    def trading(self):
        return self.exclude(group_name__startswith='real_ib')

    def real_accounts_for_forex(self):
        return self.filter(group_name__iregex=real_accounts_for_forex_regex())

    def realmicro(self):
        return self.filter(group_name__iregex=RealMicroAccountType.regex.pattern)

    def real_ib(self):
        return self.filter(group_name__startswith='real_ib')

    def realstd(self):
        return self.filter(group_name__iregex=StandardAccountType.regex.pattern)

    def by_groups(self, *include_groups):
        if not include_groups:
            return self
        return self.filter(group_name__iregex='|'.join(g.regex.pattern for g in include_groups))

    def exclude_groups(self, *exclude_groups):
        if not exclude_groups:
            return self
        return self.exclude(group_name__iregex='|'.join(g.regex.pattern for g in exclude_groups))

    def demo(self):
        return self.filter(group_name__iregex=demo_regex())

    def demo_active(self):
        return self.demo().filter(is_deleted=False)

    def non_demo(self):
        return self.exclude(group_name__iregex=demo_regex())

    def non_demo_active(self):
        return self.non_demo().filter(is_deleted=False)


class TradingAccountManager(models.Manager, CustomManagerMixin):
    # Important for using QuerySet methods on related fields
    use_for_related_fields = True

    def get_queryset(self):
        return TradingAccountQueryset(self.model)


class TradingAccount(models.Model):
    """
    User's account abstract from trading engine intrinsics.
    """
    user = models.ForeignKey(User, related_name="accounts")
    # TODO: Rename id later
    mt4_id = models.IntegerField(_("Account id"), db_column="mt4_id",
                                 help_text=_("Account ID at the trading platform"),
                                 db_index=True)
    group_name = models.CharField(_("Account type"), max_length=50, blank=True, null=True, db_column="_group")
    creation_ts = models.DateTimeField(_("Creation timestamp"), default=datetime.now)
    is_deleted = models.BooleanField(_("Account deleted"), default=False)
    is_archived = models.BooleanField(_("Account is archived"), default=False,
                                      help_text=_("Account was automatically archived"))
    deleted_comment = models.TextField(_("Deletion reason"), null=True,
                                       blank=True)
    client_agreement = models.FileField(
        upload_to=upload_to('client_agreements'), null=True, blank=True)
    partner_agreement = models.FileField(
        upload_to=upload_to('partner_agreements'), null=True, blank=True)
    registered_from_partner_domain = models.ForeignKey('referral.PartnerDomain', blank=True, null=True,
                                                       editable=False, on_delete=models.SET_NULL)

    is_fully_withdrawn = models.BooleanField(_("Fully withdrawn"), editable=False, default=False)

    REASON_CHARGEBACK = 'Needs deposit verification'
    REASON_BAD_DOCUMENT = 'Doc. verification failed'

    REASONS_CHOICES = {
        REASON_CHARGEBACK: REASON_CHARGEBACK,
        REASON_BAD_DOCUMENT: REASON_BAD_DOCUMENT,
    }
    last_block_reason = models.CharField(_("Last block reason"), null=True, blank=True,
                                         max_length=200, choices=REASONS_CHOICES.items())

    previous_agent_account = models.PositiveIntegerField(
        null=True, blank=True, editable=False,
        help_text="Used to return to previous IB",
    )
    is_agreed_managed = models.BooleanField(_("Investment agreement accepted"),
                                            editable=True, default=False)

    qualified_for_own_reward = models.BooleanField(
        default=False, editable=False,
        help_text=u"Only for IBs. During the last verification, this partner could receive IB commission for own accs"
    )
    agreement_type = models.CharField(
        u"Agreement type",
        max_length=70,
        choices=TYPE_OF_AGREEMENT,
        default=None, null=True,
        blank=True
    )

    # Added in UpTrader to decouple from MT4
    platform_type = models.CharField(
        u"Trading platform type",
        max_length=70,
        choices=TYPE_OF_PLATFORM,
        default="mt4", null=False,
        blank=False
    )

    # ugly hack - Leverage stored here because of CFH
    _leverage = models.IntegerField(_("Account leverage"), default=50)
    # and login for CFH
    _login = models.CharField(_("Login"), default=None, null=True, max_length=200)

    objects = TradingAccountManager()

    class Meta:
        ordering = ["mt4_id", "group_name"]
        unique_together = [("user", "mt4_id")]

    # @property
    # def currency(self):
    #     # type: () -> Currency
    #     """
    #     Currency of this account.
    #     """
    #     cur = get_by_group(self.group_name)
    #     return cur or USD
    currency = USD

    @property
    def trades(self):
        # type: () -> queryset_like
        """
        All trades made from this account.
        """
        return self.api.account_trades(self)

    @property
    def open_trades(self):
        # type: () -> queryset_like
        """
        Still active trades/positions.
        """
        from platforms.mt4 import NEVER
        return self.trades.filter(close_time=NEVER)

    @property
    def deferred_trades(self):
        # type: () -> queryset_like
        """
        Trades with delayed execution.
        """
        return self.api.account_deferred_trades(self)

    @property
    def closed_trades(self):
        # type: () -> queryset_like
        """
        Trades/Positions that already closed.
        """
        from platforms.mt4 import NEVER
        return self.trades.exclude(close_time=NEVER)

    def get_available_leverages(self):
        # type: () -> List[int]
        """
        Return available to this account leverages.
        """
        if not self.group:
            return []

        return self.api.account_available_leverages(self)

    @cached_property
    def is_demo(self):
        # type: () -> bool
        """Returns True if account is a demo and False otherwise."""
        log.debug("demo_regex=%s" % demo_regex())
        return bool(re.compile(demo_regex()).match(self.group_name or ""))

    @cached_property
    def is_ib(self):
        # type: () -> bool
        # Should be left as-is, and then refactored into new IB system
        """Returns True if account is an IB (partner) account and False otherwise."""
        return self.group_name and 'real_ib' in self.group_name

    @cached_property
    def is_micro(self):
        # type: () -> bool
        """
        $1.00 on Micro account is $0.01 in real life
        1 lot on Micro account is 0.01 real lot etc.
        """
        return bool(re.compile(micro_regex()).match(self.group_name or ""))

    def __unicode__(self):
        # type: () -> unicode
        """
        Unicode representstion.
        """
        if self.group:
            return u"%s (%s)" % (self.mt4_id, self.group)
        else:
            return unicode(self.mt4_id)

    @cached_property
    def group(self):
        # type: () ->  str
        """
        Account type (despite naming).
        Returns AccountType object, not string!
        """
        from platforms.cfh.exceptions import CFHError
        from platforms.strategy_store.exceptions import SSError
        try:
            return get_account_type(self.api.account_group(self))
        except (CFHError, SSError):
            return None

    @cached_property
    def api(self):
        # type: () -> object
        """
        Get module facade with platform-specific functionality.
        """
        log.debug("platform_type=%s" % self.platform_type)
        if self.platform_type == "mt4":
            from mt4 import ApiFacade
            return ApiFacade()
        # Other platforms
        elif self.platform_type == "strategy_store":
            from strategy_store import ApiFacade  # type: ignore
            return ApiFacade(settings.SS_API_HOST, settings.SS_API_LOGIN, settings.SS_API_TOKEN)
        elif self.platform_type == "cfh":
            from cfh import ApiFacade  # type: ignore
            # TODO: store servers inside accounts, because it may be random in general
            if self.is_demo:
                broker_api = settings.DEMO_CFH_API_BROKER
                clientadmin_api = settings.DEMO_CFH_API_CLIENTADMIN
                clientadmin_api_login = settings.DEMO_CFH_API_LOGIN
                clientadmin_api_passwd = settings.DEMO_CFH_API_PASSWORD
                broker_api_login = settings.DEMO_CFH_API_LOGIN
                broker_api_passwd = settings.DEMO_CFH_API_PASSWORD
            else:
                broker_api = settings.CFH_API_BROKER
                clientadmin_api = settings.CFH_API_CLIENTADMIN
                clientadmin_api_login = settings.CFH_API_LOGIN
                clientadmin_api_passwd = settings.CFH_API_PASSWORD
                broker_api_login = settings.CFH_API_LOGIN
                broker_api_passwd = settings.CFH_API_PASSWORD

            return ApiFacade(broker_api, clientadmin_api,
                             clientadmin_api_login, clientadmin_api_passwd,
                             broker_api_login, broker_api_passwd
                             )

    def save(self, **kwargs):
        # type: (**object) -> None
        """
        Delegate model saving to platform.
        """
        log.info("Saving account %d" % self.mt4_id)
        self.api.account_update(self)
        super(TradingAccount, self).save(**kwargs)

    @property
    def leverage(self):
        # type: () -> int
        """
        Credit leverage of an account.
        """
        from platforms.cfh.exceptions import CFHError
        from platforms.strategy_store.exceptions import SSError
        try:
            return self.api.account_leverage(self)
        except (CFHError, SSError):
            return '---'

    @property
    def is_disabled(self):
        # type: () -> bool
        """
        Is account disabled?
        """
        return self.api.account_disabled(self)

    @property
    def balance_money(self):
        # type: () -> Money
        """
        Return account balance in account currency.
        Returns Money object.
        """
        return self.get_balance_money(self)

    @property
    def equity_money(self):
        from platforms.cfh.exceptions import CFHError
        from platforms.strategy_store.exceptions import SSError
        # type: () -> Money
        """
        Return account equity (value of open positions + balance)
        Returns Money object.
        """
        try:
            return Money(self.api.account_equity(self), self.currency)
        except (CFHError, SSError):
            return NoneMoney()

    def check_connect(self):
        log.debug("Checking account connection for {}".format(self.mt4_id))
        return self.api.account_check_connect(self)

    def check_password(self, password):
        # type: (str) -> bool
        """
        Check account password (platform-specific).
        Returns boolean.
        """
        log.info("Changing password for account %d" % self.mt4_id)
        return self.api.account_check_password(self, password)

    def change_balance(self, amount, comment, **kwargs):
        # type: (float, unicode, **object) -> float
        """
        Change account balance by some amount (positive or negative) with comment.
        request_id & transaction_type not used for now.
        Returns changed amount (positive!), None in case of errors.
        """
        log.info("Changing balance on account %d by %.2f%s" % (self.mt4_id, amount, self.currency.symbol))
        if amount > 0:
            return self.api.account_deposit(self, abs(amount), comment=comment, **kwargs)
        else:
            return self.api.account_withdraw(self, abs(amount), comment=comment, **kwargs)

    @cached_property
    def agent_clients(self):
        # type: () -> List[User]
        """
        Clients, introduced by agent.
        Returns list of User objects.
        """
        return User.objects.filter(profile__agent_code=self.mt4_id)

    def open_orders_count(self):
        # type: () -> int
        """A shortcut for open orders count"""
        return len(self.open_trades)

    def get_history(self, start=None, end=None, opened=False, count_limit=None):
        # type: (datetime, datetime, bool, int) -> queryset_like
        """
        History of trades on account from start date to end date, which are opened or not with count_limit.
        Returns list of trades, None on errors.
        """
        log.debug("Getting history on account %d" % self.mt4_id)
        trades = self.api.account_trades(self, from_date=start or (datetime.now() - timedelta(300)),
                                         to_date=end or datetime.now())
        if opened:
            trades = trades.filter(close_time__isnull=True)
        return trades[:count_limit or sys.maxint]

    @cached_property
    def no_inout(self):
        # type: () -> bool
        """
        Determines if deposit/withdrawal operations are blocked for this account type.
        Returns boolean.
        """
        return getattr(self.group, 'no_inout', True)

    @property
    def has_restore_issue(self):
        # type: () -> bool
        """
        User has requested to restore this account from archive.
        Returns boolean.
        """
        # A shortcut for templates
        from issuetracker.models import RestoreFromArchiveIssue  # Circular import

        if not self.is_archived:
            return False
        return RestoreFromArchiveIssue.objects.filter(account=self, status="open").exists()

    def change_leverage(self, leverage_value):
        # type: (int) -> bool
        """
        Change leverage value of account in platform-specific way.
        Returns changed value, None on errors.
        """
        log.info("Changing leverage on account %d to %d", self.mt4_id, leverage_value)
        self._leverage = leverage_value
        return self.api.account_change_leverage(self, leverage_value)

    def block(self, value=True, block_reason=None):
        # type: (bool, unicode) -> None
        if value:
            log.info("Blocking account %d", self.mt4_id)
        else:
            log.info("UnBlocking account %d", self.mt4_id)
        if block_reason:
            log.info("Reason: %s" % block_reason)

        if value and block_reason not in self.REASONS_CHOICES:
            raise ValueError(u'Reason %s not in REASONS_CHOICES' % block_reason)

        if value:
            self.api.account_block(self)
            if block_reason == TradingAccount.REASON_CHARGEBACK:
                from issuetracker.models import CheckOnChargebackIssue
                if not CheckOnChargebackIssue.objects.filter(author=self.user,
                                                             status__in=("open", "processing")).exists():
                    issue = CheckOnChargebackIssue(author=self.user)
                    issue.save()
            Event.ACCOUNT_BLOCK.log(self, {"reason": block_reason})
            self.last_block_reason = block_reason
        else:
            self.api.account_unblock(self)
            Event.ACCOUNT_UNBLOCK.log(self)
            self.last_block_reason = None

        self.save()

    def change_password(self, password=None):
        # type: (str) -> str
        """
        Change password of account in platform-specific way.
        """
        log.info("Changing password for account %d" % self.mt4_id)
        if not password:
            from platforms.utils import create_password
            password = create_password()
        return self.api.account_change_password(self, password)

    def get_balance(self, currency=None, with_bonus=False):
        # type: (Currency, bool) -> Tuple[float, Currency]
        from platforms.converter import convert_currency
        try:
            balance = normalize(self, self.api.account_balance(self))
        except AttributeError:
            # catched because mt4user is None :(
            return None, None

        #if we should return value as it is, return with original currency
        if not currency:
            return balance, self.currency

        return convert_currency(balance, self.currency, currency)

    def get_balance_money(self, with_bonus=False):
        from platforms.cfh.exceptions import CFHError
        from platforms.strategy_store.exceptions import SSError
        # type: (bool) -> Money
        try:
            return Money(*self.get_balance(with_bonus=with_bonus))
        except (CFHError, SSError):
            return NoneMoney()


class AbstractTrade(models.Model):
    """
    Financial trade abstract from engine implementation.
    """
    class Commands(object):
        """
        Available types of trades.
        """
        BUY = 0
        SELL = 1
        BUY_LIMIT = 2
        SELL_LIMIT = 3
        BUY_STOP = 4
        SELL_STOP = 5
        INOUT = 6
        CREDIT = 7

    CMD_CHOICES = (
        (Commands.BUY, "BUY"),
        (Commands.SELL, "SELL"),
        (Commands.BUY_LIMIT, "BUY LIMIT"),
        (Commands.SELL_LIMIT, "SELL LIMIT"),
        (Commands.BUY_STOP, "BUY STOP"),
        (Commands.SELL_STOP, "SELL STOP"),
        (Commands.INOUT, "INOUT"),
        (Commands.CREDIT, "CREDIT"),
    )

    # Trade id (Number of order ticket)
    ticket = models.IntegerField(primary_key=True, db_column='TICKET')
    # Name of order symbol
    symbol = models.CharField(max_length=48, db_column='SYMBOL')
    # Number of digits after decimal point for the symbol
    digits = models.IntegerField(db_column='DIGITS')
    # Order type
    cmd = models.IntegerField(db_column='CMD', choices=CMD_CHOICES)
    # Number of lots in order.
    # MT4 note:
    # The value of Volume is stored on trading server as a real volume multiplied by 100.
    # Thus, if you want to get the real order volume you have to divide value in the Volume field by 100.
    # For example, if you see value 1 in the Volume field of the mt4_trades SQL table,
    # this means that the real volume of deal is 0.01.
    volume = models.IntegerField(db_column='VOLUME')
    # Time of order opening
    open_time = models.DateTimeField(db_column='OPEN_TIME')
    # Price of order opening
    open_price = models.FloatField(db_column='OPEN_PRICE')
    # Stop Loss of an order
    sl = models.FloatField(db_column='SL')
    # Take Profit of an order
    tp = models.FloatField(db_column='TP')
    # Time of order closing
    close_time = models.DateTimeField(db_column='CLOSE_TIME')
    # Expiration date and time of pending order
    expiration = models.DateTimeField(db_column='EXPIRATION')
    # Base symbol currency to deposit currency rate at time of order opening
    conv_rate1 = models.FloatField(db_column='CONV_RATE1')
    # Base symbol currency to deposit currency rate at time of order closing
    conv_rate2 = models.FloatField(db_column='CONV_RATE2')
    # Charged standard commission
    commission = models.FloatField(db_column='COMMISSION')
    # Charged agent commission
    commission_agent = models.FloatField(db_column='COMMISSION_AGENT')
    # Charged swap
    swaps = models.FloatField(db_column='SWAPS')
    # Price of order closing
    close_price = models.FloatField(db_column='CLOSE_PRICE')
    # PROFIT!!!
    profit = models.FloatField(db_column='PROFIT')
    # Charged taxes for commission
    taxes = models.FloatField(db_column='TAXES')
    # Comment for order
    comment = models.CharField(max_length=96, db_column='COMMENT')
    # Internal ID of order (this field is used in development using API)
    internal_id = models.IntegerField(db_column='INTERNAL_ID')
    # Margin recalculation rate from open order currency to deposit currency
    margin_rate = models.FloatField(db_column='MARGIN_RATE')
    # Time of order last change on trade server in UNIX format (server time)
    timestamp = models.IntegerField(db_column='TIMESTAMP')
    # Time of position modification
    modify_time = models.DateTimeField(db_column='MODIFY_TIME')

    class Meta:
        abstract = True

    def __unicode__(self):
        # type: () -> unicode
        if self.cmd == self.Commands.INOUT:
            if self.profit >= 0:
                return (u"DEPOSIT order %s at ACC%s at %s on %s"
                        % (self.comment, self.login, self.close_time, self.profit))
            else:
                return (u"WITHDRAW order %s at ACC%s at %s on %s"
                        % (self.comment, self.login, self.close_time, self.profit))
        elif self.cmd == self.Commands.CREDIT:
            return u"CREDIT order %s at ACC%s at %s" % (self.comment, self.login, self.close_time)
        else:
            return u"%s %s order at ACC%s opened at %s" % (self.get_cmd_display(), self.symbol,
                                                           self.login, self.open_time)

    objects = AdvancedManager()


class TradeQuerySet(models.QuerySet):
    """
    Query set for trades.
    Provides most recently used queries: open, closed, deferred, recent trades.
    """
    CMD = AbstractTrade.Commands
    NEVER = datetime(1970, 1, 1, 0, 0)
    RECENT_TIME = timedelta(60)  # 2 MONTHS

    def open(self):
        return self.filter(close_time=self.NEVER, cmd__in=(self.CMD.BUY, self.CMD.SELL, self.CMD.INOUT, self.CMD.CREDIT))

    def deferred(self):
        return self.filter(close_time=self.NEVER, cmd__in=(self.CMD.BUY_LIMIT, self.CMD.SELL_LIMIT, self.CMD.BUY_STOP, self.CMD.SELL_STOP))

    def closed(self):
        # type: () -> TradeQuerySet
        return self.filter(cmd__lt=8).exclude(close_time=self.NEVER)

    def recent(self):
        # type: () -> TradeQuerySet
        return self.filter(
            Q(close_time=self.NEVER)
            | Q(close_time__gte=datetime.now() - self.RECENT_TIME)
        )


class AbstractQuote(models.Model):
    """
    Symbol quote.
    """
    symbol = models.CharField(max_length=16, null=False, db_column="SYMBOL", primary_key=True)
    at_time = models.DateTimeField(null=False, db_column="TIME")
    # MODIFY_TIME - Время последнего обновления записи в БД MySQL (локальное время машины, где стоит MySQL)
    modify_time = models.DateTimeField(null=False, db_column="MODIFY_TIME")
    bid = models.FloatField(null=False, db_column="BID")
    ask = models.FloatField(null=False, db_column="ASK")
    low = models.FloatField(null=False, db_column="LOW")
    high = models.FloatField(null=False, db_column="HIGH")
    # direction - Направление движения цены Bid по сравнению с предыдущей котировкой
    # (0 - цена возросла, 1 - цена упала)
    direction = models.BooleanField(null=False, db_column="DIRECTION", default=False)
    # digits - число знаков после запятой
    digits = models.IntegerField(null=False, db_column="DIGITS")
    spread = models.IntegerField(null=False, db_column="SPREAD")

    def __unicode__(self):
        # type: () -> unicode
        return "%(pair)s growth: %(growth)s, bid: %(bid)s, ask: %(ask)s at %(date)s" % {
            "pair": self.symbol,
            "growth": "down" if self.direction else "up",
            "bid": self.bid,
            "ask": self.ask,
            "date": self.at_time,
        }

    class Meta:
        abstract = True


class ChangeQuote(models.Model):
    """
    Quotes table
    """

    # category of quotes
    category = models.CharField(_("Category name"), null=False, blank=False, max_length=30)
    # list of quotes (like: ES, EURRUB, ETC)
    quotes = models.CharField(_("List of quotes"), max_length=1024, help_text=_('Example: EURUSD, GBPUSD, AUDCAD'))

    class Meta:
        verbose_name = _('List of quotes')

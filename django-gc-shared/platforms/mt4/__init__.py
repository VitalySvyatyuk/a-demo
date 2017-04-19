# -*- coding: utf-8 -*-

from _mysql import OperationalError as MySQLOperationalError
from datetime import datetime

import math
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError as DjangoOperationalError

from platforms.converter import convert_currency
from platforms.mt4.api import MT4Error, InvalidAccount, DatabaseAPI, SocketAPI, CustomAPI
from platforms.mt4.api.utils import get_engine_name
from platforms.mt4.external.models import ChangeIssue, mt4_user, RealUser, DemoUser, ArchiveUser
from platforms.mt4.external.models_trade import RealTrade, ArchiveTrade, DemoTrade

NEVER = datetime(1970, 1, 1, 0, 0)

import logging
log = logging.getLogger(__name__)

# Register commands
import api.commands

# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic
class ApiFacade(object):
    """
    Facade provides common operations for all platform backends.
    """
    def account_update(self, account):
        """
        Update date of creation from mt4 db.
        """
        # If an account doesn't yet have creation_ts we fetch account
        # info using DatabaseAPI and check if regdate is set (which
        # is when it aint equal to the unixtime zero). If so, we then
        # update creation_ts with its value, else datetime.now() is
        # used.
        # 1/1/2000 seems to be mt4 default
        log.debug("Saving mt4 account %d" % account.mt4_id)
        if not account.creation_ts or account.creation_ts == datetime(2000, 1, 1):
            try:
                info = self._get_info("db")
            except (InvalidAccount, MT4Error):
                log.error("Invalid account!")
            else:
                if info:
                    if info.regdate > datetime(1970, 1, 1):
                        account.creation_ts = info.regdate
                    else:
                        account.creation_ts = datetime.now()

                        # Some accounts still get no creation_ts, I'm too lazy to debug why, maybe this will help
        if not account.creation_ts:
            account.creation_ts = datetime.now()
        account.save
        log.debug("creation_ts=%s" % account.creation_ts)

    def account_group(self, account):
        """
        Account group.
        Mt4-specific, should be used only to get .group for Mt4 Accs.
        """
        mt4user = self._get_mt4user(account)
        log.debug("mt4user=%s" % mt4user)
        if account.pk and account.user and mt4user is not None \
                and account.group_name != mt4user.group:
            account.group_name = mt4user.group
            account.save(update_fields=['group_name'])
        return mt4user.group if mt4user else account.group_name

    @staticmethod
    def _change_mt4_field(account, field, value, get_or_create=False):
        log.debug("Change mt4 field %s=%s on %d" % (field, value, account.mt4_id))
        if get_or_create:
            method = ChangeIssue.objects.get_or_create
        else:
            method = ChangeIssue.objects.create
        return method(login=account.mt4_id, field=field, value=value)

    def account_change_password(self, account, password):
        log.debug("Changing password for mt4 account %d" % account.mt4_id)
        self._change_mt4_field(account, 'PASSWORD', password)
        return password

    def account_change_leverage(self, account, leverage_value):
        log.debug("Changing leverage for mt4 account %d" % account.mt4_id)
        return self._change_mt4_field(account, 'LEVERAGE', leverage_value)

    def account_block(self, account):
        log.debug("Blocking mt4 account %d" % account.mt4_id)
        return self._change_mt4_field(account, 'BLOCK', 'block')

    def account_unblock(self, account):
        log.debug("UnBlocking mt4 account %d" % account.mt4_id)
        return self._change_mt4_field(account, 'BLOCK', 'unblock')

    def account_agents(self, account, demo=False):
        # Should be removed, see .agents
        api = self._get_mt4api(account, 'db', demo)
        log.debug("api=%s" % api)
        return mt4_user[api.db_name].objects.filter(agent_account=account.mt4_id).order_by('login')

    @staticmethod
    def _get_mt4api(account, mode=None, get_demo=False):
        """
        Returns Mt4 API object, based on a given mode: 'db' yields
        `DatabaseAPI` instance, and 'socket' — `SocketAPI`.
        """
        log.debug("mode=%s" % mode)
        if mode == "db":
            if get_demo:
                server = DatabaseAPI(account.mt4_id, db='demo')
            else:
                server = DatabaseAPI(account.mt4_id)
        elif mode == "db_archive":
            server = DatabaseAPI(account.mt4_id, db="db_archive")
        elif mode == "socket":
            server = SocketAPI()
        else:
            log.warn("Unknown mode!")
            raise ValueError(
                "`mode` argument should be either 'db' or 'socket'")

        return server

    def account_leverage(self, account):
        return int(self._get_mt4user(account).leverage)

    def account_check_password(self, account, password):
        api = self._get_mt4api(account, "socket")
        log.debug("Checking pass for %d" % account.mt4_id)
        log.debug("api=%s" % api)
        try:
            api.login(account.mt4_id, password)
        except (InvalidAccount, ValueError):
            log.warn("Invalid password!" )
            return False
        return True

    def _get_info(self, account, mode='db', need_normalize=False, **kwargs):
        from ..models import normalize
        # noinspection PyUnresolvedReferences
        info = self._get_mt4api(account, mode).info(**kwargs)
        log.debug("info=%s", info)

        if need_normalize:
            log.debug("Normalization")
            for attr in ('balance', 'equity', 'margin', 'credit',
                         'free', 'deposit', 'withdraw', 'profit'):
                if not hasattr(info, attr):
                    continue
                value = getattr(info, attr)
                setattr(info, attr, normalize(account, value))
        return info

    @staticmethod
    def _get_mt4user(account):
        """
        Return Mt4 User object.
        """
        engine = get_engine_name(account.mt4_id, get_demo=account.is_demo)
        log.debug("engine=%s" % engine)
        try:
            return mt4_user[engine].objects.get(login=account.mt4_id)
        except (ObjectDoesNotExist, DjangoOperationalError, MySQLOperationalError):
            log.warn("MT4 user not found! Check if settings points to right mt4 db")
            # OperationalError is for case when MySQL went down below
            return None

    def account_balance(self, account):
        mt4user = self._get_mt4user(account)
        return mt4user.balance if mt4user else None

    def account_equity(self, account):
        mt4user = self._get_mt4user(account)
        return mt4user.equity if mt4user else None

    def account_disabled(self, account):
        mt4user = self._get_mt4user(account)
        log.debug("mt4user=%s" % mt4user)
        return not bool(mt4user.enable) if mt4user else False

    def account_available_leverages(self, account):
        """
        Leverages calculation function.
        """
        group = account.group
        log.debug("group=%s" % group)
        user = (DemoUser if account.is_demo else ArchiveUser if account.is_archived else RealUser).\
            objects.filter(login=account.mt4_id).first()
        log.debug("user=%s" % user)
        return calculate_available_leverages(group, user)

    def account_trades(self, account, **kwargs):
        log.debug("Loading trades for %d" % account.mt4_id)
        if account.is_demo:
            cls = DemoTrade
        elif account.is_archived:
            cls = ArchiveTrade
        else:
            cls = RealTrade
        log.debug("cls=%s" % cls)
        return cls.objects.filter(login=account.mt4_id).order_by("open_time")

    def account_deferred_trades(self, account):
        """
        Trades with delayed execution.
        """
        return self.account_trades(account).filter(close_time=NEVER, cmd__in=(2, 3, 4, 5))

    def account_create(self, account):
        """
        Do nothing - Mt4 account creation is done through magic in mt4/forms.py
        """
        # TODO: move logic here from forms!
        pass

    def account_deposit(self, account, amount, **kwargs):
        log.debug("Depositing %.2f%s to mt4 account %d" % (amount, account.currency.symbol, account.mt4_id))
        return self._mt4_change_balance(account, +amount, **kwargs)

    def account_withdraw(self, account, amount, **kwargs):
        log.debug("Withdrawing %.2f%s from mt4 account %d" % (amount, account.currency.symbol, account.mt4_id))
        return self._mt4_change_balance(account, -amount, **kwargs)

    @staticmethod
    def _mt4_change_balance(account, amount, **kwargs):
        """
        Change balance on mt4 account through CustomAPI.
        """
        log.debug("Changing mt4 balance on %d by %s" % (account.mt4_id, amount))
        request_id = getattr(kwargs, 'request_id', 0)
        transaction_type = getattr(kwargs, 'transaction_type', '')
        credit = getattr(kwargs, 'credit', None)
        comment = getattr(kwargs, 'comment', '')
        amount_currency = account.currency
        if amount_currency:
            amount = convert_currency(amount, from_currency=amount_currency,
                                      to_currency=account.currency)[0]

        api = CustomAPI(engine=get_engine_name(account.mt4_id, get_demo=account.is_demo))
        log.debug("custom api=%s" % api)
        round_function = math.floor if amount > 0 else math.ceil
        amount = round_function(amount * 100) / 100
        return api.change_account_balance(login=account.mt4_id, amount=amount, comment=comment, request_id=request_id,
                                          transaction_type=transaction_type, credit=credit)


def calculate_available_leverages(group, user, limit=None):
    from django.utils.translation import get_language
    log.debug("lang=%s" % get_language())
    if get_language() == "id":
        leverage_limit = 2000
    else:
        leverage_limit = 500

    log.debug("limit=%s" % limit)
    if limit is not None:
        leverage_limit = min(leverage_limit, limit)

    log.debug("user=%s" % user)
    if user:
        balance = reduce(
            lambda total, acc: total + (acc.get_balance(currency="USD")[0] or 0),
            user.accounts.real_accounts_for_forex(), 0.0
        )

        if balance >= 100000:
            leverage_limit = min(leverage_limit, 25)
        elif balance >= 50000:
            leverage_limit = min(leverage_limit, 50)
        elif balance >= 10000:
            leverage_limit = min(leverage_limit, 100)
        elif balance >= 5000:
            leverage_limit = min(leverage_limit, 200)
        elif balance >= 2000:
            leverage_limit = min(leverage_limit, 500)

    return [
        leverage
        for leverage in group.leverage_choices
        if leverage <= leverage_limit
        ]

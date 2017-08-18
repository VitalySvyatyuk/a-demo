# -*- coding: utf-8 -*-

from _mysql import OperationalError as MySQLOperationalError
from datetime import datetime

import math
from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError as DjangoOperationalError

from platforms.mt4.external.models import mt4_user, RealUser, DemoUser, ArchiveUser
from platforms.mt4.external.models_trade import RealTrade, ArchiveTrade, DemoTrade

NEVER = datetime(1970, 1, 1, 0, 0)

import logging
log = logging.getLogger(__name__)
import mt4api


# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic
class ApiFacade(object):
    """
    Facade provides common operations for all platform backends.
    """
    def account_update(self, account):
        """
        Update date of creation from mt4 db.
        """
        log.debug("Saving mt4 account %d" % account.mt4_id)
        if not account.creation_ts:
            info = self._get_mt4user(account)
            if info:
                if info.regdate > datetime(1970, 1, 1):
                    account.creation_ts = info.regdate

        if not account.creation_ts:
            account.creation_ts = datetime.now()
        log.debug("creation_ts=%s" % account.creation_ts)

    def account_group(self, account):
        """
        Account group.
        Mt4-specific, should be used only to get .group for Mt4 Accs.
        """
        if not account.group_name:  # We should have at least some old account group to get engine name
            return None
        mt4user = self._get_mt4user(account)
        log.debug("mt4user=%s" % mt4user)
        if account.pk and account.user and mt4user is not None \
                and account.group_name != mt4user.group:
            account.group_name = mt4user.group
            account.save(update_fields=['group_name'])
        return mt4user.group if mt4user else account.group_name

    def account_check_connect(self, account):
        return self.get_mt4api(account).ping()

    def account_change_password(self, account, password):
        log.debug("Changing password for mt4 account %d" % account.mt4_id)
        self.get_mt4api(account).change_password(account.mt4_id, password)
        return password

    def account_change_leverage(self, account, leverage_value):
        log.debug("Changing leverage for mt4 account %d" % account.mt4_id)
        return self.get_mt4api(account).change_user_data(account.mt4_id, leverage=leverage_value)

    def account_block(self, account):
        log.debug("Blocking mt4 account %d" % account.mt4_id)
        return self.get_mt4api(account).change_user_data(account.mt4_id, enable=0)

    def account_unblock(self, account):
        log.debug("UnBlocking mt4 account %d" % account.mt4_id)
        return self.get_mt4api(account).change_user_data(account.mt4_id, enable=1)

    def account_agents(self, account, demo=False):
        # Should be removed, see .agents
        engine = self.get_engine(account)
        log.debug("engine=%s" % engine)
        return mt4_user[engine].objects.filter(agent_account=account.mt4_id).order_by('login')

    @staticmethod
    def get_engine(account):
        return "demo" if account.is_demo else "default"

    @classmethod
    def get_mt4api(cls, account):
        return mt4api.RemoteMT4Manager(engine=cls.get_engine(account))

    def account_leverage(self, account):
        mt4user = self._get_mt4user(account)
        return mt4user.leverage if mt4user else None

    def account_check_password(self, account, password):
        return self.get_mt4api(account).change_password(account.mt4_id, password)

    @classmethod
    def _get_mt4user(cls, account):
        """
        Return Mt4 User object.
        """
        engine = cls.get_engine(account)
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
        user = (DemoUser if account.is_demo else RealUser).\
            objects.filter(login=account.mt4_id).first()
        log.debug("user=%s" % user)
        return calculate_available_leverages(group, user)

    def account_trades(self, account, **kwargs):
        log.debug("Loading trades for %d" % account.mt4_id)
        if account.is_demo:
            cls = DemoTrade
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

    @classmethod
    def _mt4_change_balance(cls, account, amount, **kwargs):
        """
        Change balance on mt4 account through CustomAPI.
        """
        log.debug("Changing mt4 balance on %d by %s" % (account.mt4_id, amount))
        request_id = getattr(kwargs, 'request_id', 0)
        transaction_type = getattr(kwargs, 'transaction_type', '')
        credit = bool(getattr(kwargs, 'credit', False))
        comment = getattr(kwargs, 'comment', '')

        # api = CustomAPI(engine=get_engine_name(account.mt4_id, get_demo=account.is_demo))
        api = cls.get_mt4api(account)
        log.debug("custom api=%s" % api)
        round_function = math.floor if amount > 0 else math.ceil
        amount = round_function(amount * 100) / 100
        return api.change_balance(login=account.mt4_id, amount=amount, comment=comment, credit=credit)


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

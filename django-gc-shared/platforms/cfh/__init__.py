# -*- coding: utf-8 -*-
"""
CFH CLEARING LIMITED broker platform (cfhclearing.com).
It has SOAP-based communication API.
"""
from datetime import datetime
import sys
from random import randint

from django.conf import settings
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Error

from platforms.models import AbstractTrade, TradingAccount
from platforms.utils import create_password
from project.utils import queryset_like
from shared.decorators import cached_func
from .exceptions import CFHError

import logging
log = logging.getLogger(__name__)
CACHE_TIMEOUT = 3*60

# noinspection PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic,PyMethodMayBeStatic
class ApiFacade(object):

    def __init__(self, broker_endpoint, clientadmin_endpoint, login, password):
        """
        Api facade constructor:
        broker_endpoint - URL of CFH Broker Data WebService,
        clientadmin_endpoint - URL of CFH Client Admin WebService,
        login - CFH login,
        password - CFH password.
        """
        log.debug("Creating CFH facade for login %s" % login)
        log.debug("Enpoints: %s, %s" % (broker_endpoint, clientadmin_endpoint))
        self.client1 = Client(broker_endpoint,
                              transport=Transport(http_auth=(login, password)))
        self.client2 = Client(clientadmin_endpoint,
                              transport=Transport(http_auth=(login, password)))

        if not self.client1.service.ValidateService():
            log.error("CFH validation failed, check credentdials!")
            raise CFHError(0, "CFH broker service validation failed!")
        if not self.client2.service.ValidateService():
            log.error("CFH validation failed, check credentdials!")
            raise CFHError(0, "CFH client admin service validation failed!")

        self._load_instruments()

    def account_update(self, account):
        """
        Save existing account to remote, does nothing for CFH!
        Better change from CFH partner portal!
        ClientAdmin API only allows changing account name
        """
        pass

    def account_group(self, account):
        """
        Return account group name.
        Not stored in CFH.
        """
        return account.group_name

    def account_change_password(self, account, password):
        """
        Change cfh password, returns back password if OK, else None.
        """
        try:
            log.debug("Changing password for cfh acc %d" % account.mt4_id)
            resp = self.client2.service.GetLoginIDFromName(LoginName=account._login)
            login_id = resp
            log.debug("login_id=%d" % login_id)
            resp = self.client2.service.ChangeLoginPassword(LoginID=login_id,
                                                            NewLoginPassword=password)
            log.debug("resp=%s" % resp)
        except Error as e:
            raise CFHError(500, e.message)
        if resp:
            return password

    def account_change_leverage(self, account, leverage_value):
        """
        Change account leverage, not supported in CFH.
        """
        raise NotImplementedError("Not supported in this platform")

    def account_block(self, account):
        """
        Block account, not supported in CFH.
        """
        raise NotImplementedError("Not supported in this platform")

    def account_unblock(self, account):
        """
        UnBlock account, not supported in CFH.
        """
        raise NotImplementedError("Not supported in this platform")

    def account_agents(self, account):
        """
        Return clients, registered through this partner.
        """
        return []

    def account_check_password(self, account, password):
        """
        Check account pass, not supported in CFH.
        """
        raise NotImplementedError("Not supported in this platform")

    @cached_func(CACHE_TIMEOUT)
    def account_balance(self, account):
        """
        Get account balance, returns float.
        """
        try:
            resp = self.client1.service.GetAccountInfo(accountId=account.mt4_id)
            log.debug("resp=%s" % resp)
        except Error as e:
            raise CFHError(500, e.message)
        return resp['Balance']

    def account_equity(self, account):
        """
        Get account equity, returns float.
        """
        # raise NotImplementedError("Not supported in this platform")
        return None

    def account_disabled(self, account):
        """
        Check if account is disabled.
        """
        try:
            resp = self.client1.service.GetAccountInfo(accountId=account.mt4_id)
            log.debug("resp=%s" % resp)
        except Error as e:
            raise CFHError(500, e.message)
        return not resp['IsActive']

    def account_available_leverages(self, account):
        """
        Return supported leverages.
        """
        # cfh leverage supposed to be 100 by default
        # but can't be sure (no api method)
        return [100,75,50,33,25,20,10,5,1]

    @cached_func(CACHE_TIMEOUT)
    def account_trades(self, account, from_date=datetime(2000, 1, 1), to_date=datetime.now(), max_num=10000):
        """
        Get trades made from this account.
        Returns django queryset-like object, but not all methods may be supported.
        """
        try:
            log.debug("Loading account trades")
            resp = self.client1.service.GetTrades(accountId=account.mt4_id,
                                                  fromTime=from_date,
                                                  toTime=to_date,
                                                  pageSize=max_num, pageNumber=0)
            log.debug("resp=%s" % resp)
            trades = resp['TradesList'] if 'TradesList' in resp else None
            trades = trades['TradeInfo'] if trades and 'TradeInfo' in trades else []
        except Error as e:
            raise CFHError(500, e.message)
        return queryset_like(AbstractTrade, [self._convert_trade(t) for t in trades])

    def account_deferred_trades(self, account):
        """
        Get trades with deffered execution.
        Returns django queryset-like object, but not all methods may be supported.
        """
        return queryset_like(AbstractTrade, [])

    def account_create(self, account, initial_balance=0):
        """
        Create new account at CFH with initial_balance.
        Returns None if account already exists, else new account.
        """
        mail = account.user.email
        login = account.user.username
        password = create_password()
        num = randint(0, sys.maxint)
        log.debug("Creating cfh account for {0} with {1} {2}".format(login, initial_balance, account.currency.symbol))
        try:
            log.debug('leverage=%s' % account._leverage)
            client_temp = settings.CFH_CLIENT_TEMPLATES[account._leverage]
            log.debug('cl_templ=%s' % client_temp)
            resp = self.client2.service.CreateClientFromTemplate(TemplateID=client_temp,
                                                                 BrokerID=settings.CFH_BROKER_ID,
                                                                 ClientDisplayName=account.user.get_full_name(),
                                                                 LoginName=login+str(num),
                                                                 LoginPassword=password)
            log.debug("resp=%s" % resp)
            new_id = resp['ClientAccountID']
            log.debug("new_id=%d" % new_id)
            account.mt4_id = new_id
            account._login = login+str(num)
            if initial_balance:
                self.account_deposit(account, initial_balance, "Initial balance")
            return password
        except Error as e:
            raise CFHError(500, e.message)

    def account_deposit(self, account, amount, comment="", **kwargs):
        """
        Transfer amount to account with comment.
        """
        try:
            resp = self.client2.service.DepositFundsTransaction(AccountID=account.mt4_id,
                                                                ContraAccountID=settings.CFH_DEPOSIT_ACCOUNT_ID,
                                                                Amount=amount,
                                                                Currency=account.currency.slug,
                                                                Comment=comment)
            log.debug("resp=%s" % resp)
        except Error as e:
            raise CFHError(500, e.message)

    def account_withdraw(self, account, amount, comment="", **kwargs):
        """
        withdraw amount from account with comment.
        """
        try:
            resp = self.client2.service.WithdrawFundsTransaction(AccountID=account.mt4_id,
                                                                 ContraAccountID=settings.CFH_DEPOSIT_ACCOUNT_ID,
                                                                 Amount=-amount,
                                                                 Currency=account.currency.slug,
                                                                 Comment=comment)
            log.debug("resp=%s" % resp)
        except Error as e:
            raise CFHError(500, e.message)

    def account_leverage(self, account):
        """
        Return account leverage.
        """
        return account._leverage

    def _convert_trade(self, t):
        """
        Converts xml to AbstractTrades.
        """
        volume = t['Amount']
        ticket = t['BoTradeId']
        symbol = self._symbol_for(t['InstrumentId'])
        digits = None
        cmd = self._cmd_for(t['Side'])
        open_time = t['ExecutionDate']
        open_price = t['Price']
        sl = None
        tp = None
        expiration = None
        conv_rate1 = t['ConversionRate']
        conv_rate2 = conv_rate1
        commission = t['Commission']
        commission_agent = None
        swaps = None
        close_price = None  # TODO: investigate!
        close_time = None
        profit = None
        taxes = None
        comment = ''
        internal_id = t['TsTradeId']
        margin_rate = None
        timestamp = None
        modify_time = None
        # to make constructor work
        del self, t
        return AbstractTrade(**locals())

    @staticmethod
    def _cmd_for(s):
        """
        Convert trade direction.
        """
        return AbstractTrade.Commands.BUY if s == 0 else AbstractTrade.Commands.SELL

    def _symbol_for(self, i):
        """
        Convert traded symbol.
        """
        return self.instruments[i]

    def _load_instruments(self):
        """
        Load instruments from CFH.
        """
        try:
            resp = self.client1.service.GetInstruments()['InstrumentInfo']
            log.debug("resp=%s" % resp)
            self.instruments = dict((i['InstrumentId'], i['InstrumentSymbol']) for i in resp)
            log.debug("# of instruments=%d" % len(self.instruments))
        except Error as e:
            raise CFHError(500, e.message)

# -*- coding: utf-8 -*-
"""
Strategy Store (http://strategystore.org) broker platform.
"""
import requests
from hashlib import sha256
from datetime import datetime
from json import dumps
from random import randint
from requests.exceptions import ConnectionError

from project.utils import queryset_like
from .exceptions import SSError
from platforms.utils import create_password
from platforms.models import AbstractTrade
from django.utils.dateparse import parse_datetime
from shared.decorators import cached_func 

import logging
log = logging.getLogger(__name__)
CACHE_TIMEOUT = 30
HTTP_TIMEOUT = 5


class ApiFacade(object):
    """
    Facade provides common operations for all platform backends.
    """

    def __init__(self, endpoint, login, password, timeout=5):
        """
        Api facade constructor:
        endpoint - StrategyStore REST api endpoint,
        login - StrategyStore login,
        password - StrategyStore token.
        You may specify optional http requests timeout.
        """
        log.debug("Creating ss account for %s" % login)
        self.endpoint = endpoint
        self.login = login
        self.passwd = password
        self.timeout = HTTP_TIMEOUT

    def make_request(self, func, path, params):
        """
        Make HTTP request with SS authorization.
        Returns server response.
        """
        salt = str(datetime.now())
        headers = {'Authorization-Name': self.login, 'Authorization-Token': sha256(self.passwd + salt).hexdigest(),
                   'Authorization-Salt': salt, 'Content-Type': 'application/json'}
        log.debug("Making %s request to %s" % (func, path))
        log.debug("headers=%s" % headers)
        log.debug("params=%s" % params)
        try:
            # POST request
            if func == requests.post:
                return func(self.endpoint + '/' + path, data=dumps(params), timeout=self.timeout, verify=False,
                                headers=headers)
            # GET request
            else:
                return func(self.endpoint + '/' + path, params=params, timeout=self.timeout, verify=False,
                            headers=headers)
        except ConnectionError:
            raise SSError(0, 'Connection to StrategyStore failed!')

    def account_check_connect(self):
        try:
            resp = requests.head(self.endpoint)
            if not resp.ok:
                raise SSError(0, 'Connection to StrategyStore failed!')
        except ConnectionError:
            raise SSError(0, 'Connection to StrategyStore failed!')

    def account_update(self, account):
        """
        Save changed client to SS.
        """
        log.debug("Saving SS account %d" % account.mt4_id)
        resp = self.make_request(requests.post, 'api/v1/clients/editClient',
                                 {'Login': account.user.email, 'Email': account.user.email,
                                  'ExternalPartnerReference': account.user.profile.agent_code,
                                  'ID': account.mt4_id, 'FirstName': account.user.first_name,
                                  'LastName': account.user.last_name,
                                  'Mobile': account.user.profile.phone_mobile or account.user.profile.phone_work})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)

    def account_group(self, account):
        # Not stored in SS
        return account.group_name

    def account_change_password(self, account, password):
        """
        Change account password.
        Returns back password if OK, else None.
        """
        log.debug("Changing SS account password")
        resp = self.make_request(requests.post, 'api/v1/clients/{id}/resetPassword'.format(id=account.mt4_id),
                                 {'Password': password})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        json = resp.json()
        if not resp.ok:
            log.error('HTTP code: %d', resp.status_code)
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        if json['errCode'] == 0:
            return password
        else:
            raise SSError(json['errCode'], json['errMsg'])

    def account_change_leverage(self, account, leverage_value):
        raise NotImplementedError('Not supported on this platform')

    def account_block(self, account):
        raise NotImplementedError('Not supported on this platform')

    def account_unblock(self, account):
        raise NotImplementedError('Not supported on this platform')

    def account_agents(self, account):
        return []

    def account_leverage(self, account):
        # It seems that leverages are not available at all in SS
        return 1

    def account_check_password(self, account, password):
        """
        Check account password.
        Returns bool.
        """
        resp = self.make_request(requests.post, 'api/v1/clients/{id}/checkPassword'.format(id=account.mt4_id),
                                 {'Password': password})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        return resp.json()['PasswordValid']

    @cached_func(CACHE_TIMEOUT)
    def account_balance(self, account):
        resp = self.make_request(requests.get, 'api/v1/clients/{id}'.format(id=account.mt4_id), {})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        return resp.json()['Accounts'][0]['NotInvested']

    @cached_func(CACHE_TIMEOUT)
    def account_equity(self, account):
        # Since Strategy store have not implement account equity return main balance
        return self.account_balance(account)
        # resp = self.make_request(requests.get, 'api/v1/clients/{id}'.format(id=account.mt4_id), {})
        # log.debug("resp=%s %s" % (resp.status_code, resp.text))
        # if not resp.ok:
        #     raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        # return resp.json()['Accounts'][0]['Balance']

    def account_disabled(self, account):
        # SS can only stop transfers to account
        return False

    def account_available_leverages(self, account):
        # SS does not support leverages at all
        return [1]

    @cached_func(CACHE_TIMEOUT)
    def account_trades(self, account, from_date=datetime(2000, 1,1 ), to_date=datetime.now(), **kwargs):
        """
        Return all trades on account.
        """
        log.debug("Loading StrategyStore account trades")
        return self.account_open_trades(account, from_date, to_date) + self.account_closed_trades(account, from_date, to_date)

    @cached_func(CACHE_TIMEOUT)
    def account_open_trades(self, account, from_date=datetime(2000, 1, 1), to_date=datetime.now()):
        """
        Return trades with open positions at account.
        """
        params = {'MinDT': str(from_date.date()), 'MaxDT': str(to_date.date())}
        resp = self.make_request(requests.get, 'api/v3/accounts/{id}/get-open-positions'.format(id=account.mt4_id), params)
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        return queryset_like(AbstractTrade, [self._convert_trade(t) for t in resp.json()['Positions']])

    @cached_func(CACHE_TIMEOUT)
    def account_closed_trades(self, account, from_date=datetime(2000, 1, 1), to_date=datetime.now()):
        """
        Return trades with closed positions on account.
        """
        params = {'MinDT': str(from_date.date()), 'MaxDT': str(to_date.date())}
        resp = self.make_request(requests.get, 'api/v3/accounts/{id}/get-closed-positions'.format(id=account.mt4_id), params)
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        return queryset_like(AbstractTrade, [self._convert_trade(t) for t in resp.json()['Positions']])

    def account_deferred_trades(self, account):
        """
        Return deffered trades. Not in SS.
        """
        return []

    def account_create(self, account, initial_balance=0):
        """
        Create SS account with initial_balance.
        """
        password = create_password()
        log.debug("Creating StrategyStore account")
        resp = self.make_request(requests.post, 'api/v1/clients/newClientWithAccount',
                                 {'CompanyID': 1, 'LanguageID': 1, 'Login': account.user.email,
                                  'ExternalPartnerReference': account.user.profile.agent_code,
                                  'InitialBalance': initial_balance,
                                  'Password': password,
                                  'FirstName': account.user.first_name,
                                  'LastName': account.user.last_name,
                                  'ClientID': account.user.id,
                                  # 'Comment': 'DEMO' if account.is_demo else 'REAL',
                                  'Mobile': account.user.profile.phone_mobile or account.user.profile.phone_work,
                                  'Email': account.user.email,
                                  })
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        json = resp.json()
        if json['errCode'] == 0:
            return password
        else:
            raise SSError(json['errCode'], json['errMsg'])

    def account_deposit(self, account, amount, comment="", **kwargs):
        """
        Deposit SS account with amount and comment.
        """
        log.debug("Depositing %d with %f" % (account.mt4_id, amount))
        resp = self.make_request(requests.post, 'api/v1/clients/{id}/fundAccount'.format(id=account.mt4_id),
                                 {'IDAccount': account.mt4_id, 'Money': amount, 'Comment': comment, 'IsCredit': 0})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        json = resp.json()
        if json['errCode']:
            raise SSError(json['errCode'], json['errMsg'])

    def account_withdraw(self, account, amount, comment="", **kwargs):
        """
        Withdraw SS account with amount and comment.
        """
        log.debug("Withdrawing %d with %f" % (account.mt4_id, amount))
        resp = self.make_request(requests.post, 'api/v1/clients/{id}/withdrawAccount'.format(id=account.mt4_id),
                                 {'IDAccount': account.mt4_id, 'Money': amount, 'Comment': comment, 'IsCredit': 0})
        log.debug("resp=%s %s" % (resp.status_code, resp.text))
        if not resp.ok:
            raise SSError(resp.status_code, 'HTTP code not OK (%d)' % resp.status_code)
        json = resp.json()
        if json['errCode']:
            raise SSError(json['errCode'], json['errMsg'])

    def _convert_trade(self, t):
        """
        Convert trade from json to AbstractTrade.
        """
        volume = t['Lot']
        ticket = t['TradeID']
        symbol = t['Symbol']
        digits = t['PointPrecision']
        cmd = self._cmd_for(t['Type'])
        open_time = parse_datetime(t['Opened'])
        open_price = t['OpenPrice']
        sl = t['SL']
        tp = t['TP']
        expiration = None
        conv_rate1 = None
        conv_rate2 = conv_rate1
        commission = None
        commission_agent = None
        swaps = t['Swap']
        close_price = t['ClosePrice']
        close_time = parse_datetime(t['Closed'])
        profit = t['Profit']
        taxes = None
        comment = ''
        internal_id = t['ID']
        margin_rate = None
        timestamp = None
        modify_time = None
        del self, t
        return AbstractTrade(**locals())

    def _cmd_for(self, s):
        """
        Convert trade direction.
        """
        return AbstractTrade.Commands.BUY if s == 0 else AbstractTrade.Commands.SELL

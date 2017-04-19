# -*- coding: utf-8 -*-
"""
Test SS account.
"""
import unittest
from django.test import TestCase

from platforms.strategy_store import forms
from currencies import currencies
from platforms.factories import TradingAccountFactory

GROUP_NAME = forms.GROUP_NAME

class TestAccountSS(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = TradingAccountFactory(group_name=GROUP_NAME,
                                            platform_type="strategy_store", mt4_id=123)

    def test_create(self):
        # TODO: better test creation on server!
        # TODO: forms
        self.assertIsNotNone(self.account)
        self.assertIsNotNone(self.account.user)

    def test_unicode(self):
        self.assertEquals(unicode(self.account), "%d (Demo [Strategy Store])" % self.account.mt4_id)

    def test_group(self):
        self.assertIsNotNone(self.account.group)
        self.assertEquals(self.account.group.slug, "demostandard_ss")

    def test_currency(self):
        assert self.account.currency == currencies.USD

    def test_trades(self):
        self.assertGreater(len(self.account.trades), 0)

    def test_leverages(self):
        self.assertEquals([1], self.account.get_available_leverages())

    def test_is_demo(self):
        self.assertTrue(self.account.is_demo)

    def test_is_ib(self):
        self.assertFalse(self.account.is_ib)

    def test_is_micro(self):
        self.assertFalse(self.account.is_micro)

    def test_block(self):
        with self.assertRaises(NotImplementedError):
            self.account.block(block_reason='Needs deposit verification')

    def test_open_trades(self):
        self.assertGreater(len(self.account.open_trades), 0)

    def test_closed_trades(self):
        trades = self.account.closed_trades
        self.assertGreater(len(trades), 0)
        self.assertIsNotNone(trades[0].symbol)
        self.assertGreater(trades[0].volume, 0)

    def test_api(self):
        from platforms.strategy_store import ApiFacade
        self.assertTrue(isinstance(self.account.api, ApiFacade))

    def test_save(self):
        self.account.save()

    def test_leverage(self):
        self.assertEquals(self.account.leverage, 1)

    def test_disabled(self):
        self.assertFalse(self.account.is_disabled)

    def test_balance_money(self):
        balance = self.account.balance_money
        self.assertEquals(balance.amount, 1000)
        self.assertEquals(balance.currency, self.account.currency)

    @unittest.skip("Not implemented at their side")
    def test_equity_money(self):
        equity = self.account.equity_money()
        self.assertEquals(equity.amount, 0)
        self.assertEquals(equity.currency, self.account.currency)

    def test_check_password1(self):
        self.assertFalse(self.account.check_password('bad_pass'))

    def test_check_password2(self):
        self.assertTrue(self.account.check_password('qwert123'))

    def test_agent_clients(self):
        self.assertEquals(len(self.account.agent_clients), 0, "Johnie is not agent!")

    def test_open_orders_count(self):
        self.assertGreater(self.account.open_orders_count(), 0)

    def test_no_inout(self):
        self.assertFalse(self.account.no_inout)

    def test_has_restore_issue(self):
        self.assertFalse(self.account.has_restore_issue)

    def test_change_leverage(self):
        with self.assertRaises(NotImplementedError):
            self.account.change_leverage(100)

    def test_change_password(self):
        self.assertEquals(self.account.change_password('qwert123'), 'qwert123')

# -*- coding: utf-8 -*-
"""
Testing CFH account.
"""
import unittest
import fudge
from platforms.cfh import forms
from django.test import TestCase
from platforms.factories import TradingAccountFactory
from currencies import currencies

GROUP_NAME = forms.GROUP_NAME


class TestAccountCFH(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = TradingAccountFactory(group_name=GROUP_NAME,
                                            platform_type="cfh", mt4_id=120091)

    def test_unicode(self):
        self.assertEquals(unicode(self.account), "%d (Demo [CFH])" % self.account.mt4_id)

    def test_group(self):
        self.assertIsNotNone(self.account.group)
        self.assertEquals(self.account.group.slug, "demostandard_cfh")

    def test_currency(self):
        self.assertEquals(self.account.currency, currencies.USD)

    def test_trades(self):
        trades = self.account.trades
        self.assertGreater(len(trades), 0, "There are loss trades")
        self.assertGreater(len(trades), 0)
        self.assertIsNotNone(trades[0].symbol)
        self.assertGreater(trades[0].volume, 0)

    def test_leverages(self):
        self.assertEquals([100], self.account.get_available_leverages())

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
        self.assertGreaterEqual(len(self.account.open_trades), 0, "There are trades")

    def test_closed_trades(self):
        self.assertGreaterEqual(len(self.account.closed_trades), 0)

    def test_api(self):
        from platforms.cfh import ApiFacade
        self.assertTrue(isinstance(self.account.api, ApiFacade))

    def test_save(self):
        self.account.save()

    def test_leverage(self):
        self.assertEquals(self.account.leverage, 100)

    def test_disabled(self):
        self.assertFalse(self.account.is_disabled)

    def test_balance_money(self):
        balance = self.account.balance_money
        self.assertEquals(balance.amount, 124456)
        self.assertEquals(balance.currency, self.account.currency)

    def test_equity_money(self):
        with self.assertRaises(NotImplementedError):
            equity = self.account.equity_money
            self.assertEquals(equity.amount, 0)
            self.assertEquals(equity.currency, self.account.currency)

    def test_check_password1(self):
        with self.assertRaises(NotImplementedError):
            self.assertFalse(self.account.check_password('bad_pass'))

    def test_check_password2(self):
        with self.assertRaises(NotImplementedError):
            self.assertTrue(self.account.check_password('qwert123'))

    def test_agent_clients(self):
        self.assertEquals(len(self.account.agent_clients), 0, "Johnie is not agent!")

    def test_no_inout(self):
        self.assertFalse(self.account.no_inout)

    def test_has_restore_issue(self):
        self.assertFalse(self.account.has_restore_issue)

    def test_change_leverage(self):
        with self.assertRaises(NotImplementedError):
            self.account.change_leverage(100)

    @unittest.skip("Broken at CFH")
    def test_change_password(self):
        self.assertEquals(self.account.change_password('qwert123'), 'qwert123')

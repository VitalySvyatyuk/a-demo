# -*- coding: utf-8 -*-
"""
Testing MT4 account.
"""
import unittest
import fudge
from django.test import TestCase

from currencies import currencies
from platforms.factories import TradingAccountFactory
from platforms.models import TradingAccount


@unittest.skip("Cant mock MT4 server")
class TestAccountMT4(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = TradingAccountFactory(platform_type="mt4", group_name="demostd_test")

    def test_create(self):
        assert self.account
        assert self.account.user

    def test_unicode(self):
        self.assertEquals(unicode(self.account), "%d (Demo)" % self.account.mt4_id)

    def test_group(self):
        self.assertIsNotNone(self.account.group)
        self.assertEquals(self.account.group.slug, "demostandard")

    def test_currency(self):
        assert self.account.currency == currencies.USD

    def test_trades(self):
        self.assertGreater(len(self.account.trades), 0, "There must be trades")

    def test_leverages(self):
        self.assertEquals([100, 75, 66, 50, 33, 25, 20, 15, 10, 5, 3, 2, 1], self.account.get_available_leverages())

    def test_is_demo(self):
        self.assertTrue(self.account.is_demo)

    def test_is_ib(self):
        self.assertFalse(self.account.is_ib)

    def test_is_micro(self):
        self.assertFalse(self.account.is_micro)

    @fudge.patch('platforms.mt4.ApiFacade._change_mt4_field',
                 'log.models.Event.log')
    def test_block(self, fake_change_mt4_field, fake_log):
        fake_change_mt4_field.is_callable()
        fake_log.is_callable()

        account = self.account
        self.assertIsNone(account.last_block_reason)

        account.block(block_reason=TradingAccount.REASON_CHARGEBACK)
        self.assertEqual(account.last_block_reason, TradingAccount.REASON_CHARGEBACK)

        account.block(block_reason=TradingAccount.REASON_BAD_DOCUMENT)
        self.assertEqual(account.last_block_reason, TradingAccount.REASON_BAD_DOCUMENT)

        account.block(value=False)
        self.assertIsNone(account.last_block_reason)

        with self.assertRaises(ValueError):
            account.block(block_reason=None)

    def test_open_trades(self):
        self.assertEquals(len(self.account.open_trades), 0, "There must be no open trades")

    def test_closed_trades(self):
        self.assertGreater(len(self.account.closed_trades), 0, "There must be closed trades")

    def test_deferred_trades(self):
        self.assertEquals(len(self.account.deferred_trades), 0, "There must be no delay trades")

    def test_api(self):
        from platforms.mt4 import ApiFacade
        self.assertTrue(isinstance(self.account.api, ApiFacade))

    def test_save(self):
        pass

    def test_leverage(self):
        self.assertGreater(self.account.leverage, 1)

    def test_disabled(self):
        self.assertFalse(self.account.is_disabled)

    def test_balance_money(self):
        balance = self.account.balance_money
        self.assertGreaterEqual(balance.amount, 0)
        self.assertEquals(balance.currency, self.account.currency)

    def test_equity_money(self):
        equity = self.account.equity_money
        self.assertGreaterEqual(equity.amount, 0)
        self.assertEquals(equity.currency, self.account.currency)

    @unittest.skip("Wont work on local machine")
    def test_check_password1(self):
        self.assertTrue(self.account.check_password('qwert123'))

    @unittest.skip("Wont work on local machine")
    def test_check_password2(self):
        self.assertFalse(self.account.check_password('baddd'))

    def test_agent_clients(self):
        self.assertEquals(len(self.account.agent_clients), 0)

    def test_noinout(self):
        self.assertFalse(self.account.no_inout)

    def test_has_restore_issue(self):
        self.assertFalse(self.account.has_restore_issue)

    def test_change_leverage(self):
        self.assertIsNotNone(self.account.change_leverage(10))

    def test_change_password(self):
        self.assertEquals(self.account.change_password('qwert123'), 'qwert123')

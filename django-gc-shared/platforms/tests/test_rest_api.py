# -*- coding: utf-8 -*-
"""
Testing account REST API.
"""
import unittest

from django.test import TestCase
from rest_framework.test import APIClient
from platforms.factories import TradingAccountFactory


@unittest.skip('WIP')
class TestRest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.account = TradingAccountFactory(platform_type="mt4", group_name="demostd_test")
        cls.account.save()
        from profiles.factories import UserFactory
        user = UserFactory()
        user.set_password("test")
        user.save()
        cls.client = APIClient()
        cls.client.login(login=user.username, password='test')

    def test_recover_password(self):
        resp = self.client.post('/account/%d/recover_password' % self.account.mt4_id)
        self.assertEquals(resp.status_code, 200)
        # TODO: check console?

    def test_change_leverage(self):
        resp = self.client.post('/account/%d/change_leverage' % self.account.mt4_id,
                                data={'leverage': 10}, format='json')
        self.assertEquals(resp.status_code, 200)

    def test_restore(self):
        resp = self.client.post('/account/%d/restore' % self.account.mt4_id)
        self.assertEquals(resp.status_code, 200)

    def test_agents(self):
        resp = self.client.post('/account/%d/agents' % self.account.mt4_id)
        self.assertEquals(resp.status_code, 200)

    def test_demo_deposit(self):
        resp = self.client.post('/account/%d/demo_deposit' % self.account.mt4_id,
                                data={'value': 1000}, format='json')
        self.assertEquals(resp.status_code, 200)

    def test_list(self):
        resp = self.client.get('/account/list', format='json')
        self.assertEquals(resp.status_code, 200)

    def test_retrive(self):
        resp = self.client.get('/account/%d' % self.account.mt4_id, format='json')
        self.assertEquals(resp.status_code, 200)
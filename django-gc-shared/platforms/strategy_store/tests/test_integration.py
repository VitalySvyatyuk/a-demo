# -*- coding: utf-8 -*-
"""
Test basic integration with Strategy Store.
Using https://148.251.86.220:81/help
"""
from unittest import TestCase
from datetime import datetime
import requests
from hashlib import sha256
from settings import SS_API_HOST, SS_API_LOGIN, SS_API_TOKEN


def prepare_hash(token, salt):
    return sha256(token + salt).hexdigest()


class TestBasicFunc(TestCase):
    salt = str(datetime.now())

    def test_client(self):
        john = requests.get(SS_API_HOST + "api/v1/clients/123", timeout=10, verify=False, headers={
            "Content-Type": "application/json", "Authorization-Token" : prepare_hash(SS_API_TOKEN, self.salt),
            "Authorization-Name": SS_API_LOGIN, "Authorization-Salt": self.salt }).json()
        self.assertEquals(john["ID"], 123)
        self.assertIsNotNone(john["Email"])
        self.assertGreater(len(john["Accounts"]), 0)

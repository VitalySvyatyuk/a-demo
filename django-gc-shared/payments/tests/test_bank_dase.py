# -*- coding: utf-8 -*-
from django.test import TestCase
from payments.systems.bankbase import validate_iban


class TestBankDase(TestCase):

    def test_bank_account_validation_right(self):
        r = validate_iban("GB82 WEST 1234 5698 7654 32")
        self.assertTrue(r)

    def test_bank_account_validation_wrong(self):
        r = validate_iban("GB82 WEST 1334 5698 7654 32")
        self.assertFalse(r)

    def test_bank_account_validation_none(self):
        with self.assertRaises(AssertionError):
            r = validate_iban(None)

    def test_bank_account_validation_empty(self):
        with self.assertRaises(AssertionError):
            r = validate_iban("")

# -*- coding: utf-8 -*-

from django.utils import unittest

import currencies.currencies as c


class TestCurrencies(unittest.TestCase):

    def tearDown(self):
        c.Currency.register.pop("KUKU", None)

    def test_get_currency(self):
        r = c.get_currency("USD")
        self.assertEqual(r, c.USD)

        r = c.get_currency("KUKU")
        self.assertEqual(r, None)

        r = c.get_currency("KUKU", create=True)
        self.assertEqual(r, c.Currency.register["KUKU"])

    def test_has_all_attributes(self):
        attrs = ["slug", "verbose_name", "group_regex", "instrument_name", "symbol"]

        r = c.get_currency("USD")
        self.assertTrue(all(map(lambda a: hasattr(r, a), attrs)))

        r = c.get_currency("KUKU")
        self.assertFalse(all(map(lambda a: hasattr(r, a), attrs)))

if __name__ == '__main__':
    unittest.main()

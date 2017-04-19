# -*- coding: utf-8 -*-

import fudge
from django.utils import unittest

from currencies.currencies import USD
from currencies.money import Money


class TestMoney(unittest.TestCase):

    def test_should_be_0_USD_if_object_is_empty(self):
        self.assertEqual(Money().amount, 0)
        self.assertIsNotNone(Money().currency)
        self.assertEqual(Money().currency.slug, 'USD')

    def test_should_convert_any_currency_argument_to_currency_object(self):
        self.assertEqual(Money(1, 'USD').currency, USD)
        self.assertEqual(Money(1, USD).currency, USD)

    def test_should_take_negative_values(self):
        self.assertEqual(Money(-1, 'USD').amount, -1)
        self.assertEqual(Money(-100000, 'USD').amount, -100000)

    def test_should_display_properly(self):
        self.assertEqual(Money(100, 'USD').display(), USD.display_amount(100))

    def test_should_display_on_unicode(self):
        self.assertEqual(unicode(Money(100, 'USD')), Money(100, 'USD').display())

    @fudge.patch('currencies.money.convert_currency')
    def test_should_convert_with_prefix_to(self, convert_currency):
        convert_currency.is_callable().returns((99, None))
        self.assertEqual(Money(100, 'USD').to_USD().amount, 100)
        self.assertEqual(Money(100, 'USD').to_RUR().amount, 99)

    @fudge.patch('currencies.money.convert_currency')
    def test_should_create_new_object_on_covertion(self, convert_currency):
        convert_currency.is_callable().returns((99, None))
        m = Money(100, 'USD')
        self.assertNotEqual(id(m.to_RUR()), id(m))

    def test_should_create_new_object_on_covertion_even_with_same_currency(self):
        m = Money(100, 'USD')
        self.assertNotEqual(id(m.to_USD()), id(m))

    def test_should_not_allow_to_compare_different_currencies(self):
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') > Money(100, 'RUB')
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') < Money(100, 'RUB')
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') >= Money(100, 'RUB')
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') <= Money(100, 'RUB')
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') == Money(100, 'RUB')
        with self.assertRaises(NotImplementedError):
            Money(100, 'USD') != Money(100, 'RUB')

    def test_should_allow_to_compare_same_currencies(self):
        self.assertEqual(Money(100, 'USD'), Money(100, 'USD'))
        self.assertGreater(Money(100, 'USD'), Money(9, 'USD'))
        self.assertGreaterEqual(Money(100, 'USD'), Money(100, 'USD'))
        self.assertLess(Money(100, 'USD'), Money(768, 'USD'))
        self.assertLessEqual(Money(100, 'USD'), Money(100, 'USD'))
        self.assertNotEqual(Money(100, 'USD'), Money(12, 'USD'))

    def test_should_create_new_instances_on_comparisons(self):
        a, b = Money(100, 'USD'), Money(3, 'USD')
        ab_ids = map(id, [a, b])
        self.assertNotIn(id(a > b), ab_ids)
        self.assertNotIn(id(a < b), ab_ids)
        self.assertNotIn(id(a >= b), ab_ids)
        self.assertNotIn(id(a <= b), ab_ids)
        self.assertNotIn(id(a == b), ab_ids)
        self.assertNotIn(id(a != b), ab_ids)

    def test_should_support_negative(self):
        a = Money(100, 'USD')
        self.assertEqual((-a).amount, -100)
        self.assertNotEqual(id(-a), id(a))

    def test_should_support_positive(self):
        a = Money(-100, 'USD')
        self.assertEqual((+a).amount, +(-100))
        self.assertNotEqual(id(+a), id(a))

    def test_should_support_add(self):
        a, b = Money(-100, 'USD'), Money(30, 'USD')
        self.assertEqual(a + b, Money(-70, 'USD'))

    def test_should_support_sub(self):
        a, b = Money(-100, 'USD'), Money(30, 'USD')
        self.assertEqual(a - b, Money(-130, 'USD'))

    def test_should_support_mul(self):
        a, b = Money(10, 'USD'), Money(30, 'USD')
        self.assertEqual(a * b, Money(300, 'USD'))

    def test_should_support_div(self):
        a, b = Money(190, 'USD'), Money(19, 'USD')
        self.assertEqual(a / b, Money(10, 'USD'))

if __name__ == '__main__':
    unittest.main()

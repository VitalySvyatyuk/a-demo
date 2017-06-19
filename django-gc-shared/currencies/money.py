# -*- coding: utf-8 -*-
from currencies import get_currency, USD
from functools import partial
from decimal import Decimal
from platforms.converter import convert_currency
from copy import copy
from contextlib import contextmanager


class NoneMoney(object):
    """
    Used instead of Money when an error occurs. Supports a subset of Money's methods
    """
    amount = None
    currency = None

    def __str__(self):
        return self.display()

    def __unicode__(self):
        return self.display()

    def display(self, *args, **kwargs):
        return "---"

    def to(self, *args, **kwargs):
        return self

    def __getattr__(self, name):
        if name.startswith('to_'):
            # because must be callable!
            return lambda: self
        else:
            raise AttributeError

    def __nonzero__(self):
        return False


class Money(object):
    u"""
    Used to hold amounts and their currency

    amount is stored as float

    supports currency conversions:
        Money.to("USD") or Money.to_USD
    """
    __slots__ = ['amount', 'currency']
    _convert_cache_key = None

    @staticmethod
    @contextmanager
    def convert_cache_key(key):
        """
        Helper to setup cache key for currency converter using `with`
        """
        Money._convert_cache_key = key
        yield
        Money._convert_cache_key = None

    def __new__(cls, amount=0, currency=USD):
        if amount is None:
            return NoneMoney()
        return super(Money, cls).__new__(cls)

    def __init__(self, amount=0, currency=USD):
        if not isinstance(amount, (float, int, Decimal)):
            raise TypeError("Not supported amount type {0}, should be float, int or Decimal.".format(type(amount)))
        self.amount, self.currency = float(amount), get_currency(currency)

    def __getattr__(self, name):
        if name.startswith('to_'):
            to_currency = get_currency(name[3:])
            if not to_currency:
                raise AttributeError("Cannot find currency with name '{0}'".format(to_currency))
            return partial(self.to, to_currency)
        else:
            raise AttributeError

    def to(self, currency, for_date=None, cache_key=None):
        currency = get_currency(currency)  # ensure currency object
        if self.currency == currency:
            return copy(self)
        try:
            amount = float(convert_currency(
                self.amount,
                from_currency=self.currency,
                to_currency=currency,
                for_date=for_date,
                cache_key=cache_key or self._convert_cache_key)[0])
        except Exception as e:
            from django.conf import settings
            if not settings.DEBUG:
                raise e
            print e
            return NoneMoney()
        return Money(amount, currency)

    def display(self, *args, **kwargs):
        if self.currency: 
            return self.currency.display_amount(self.amount, *args, **kwargs) 
        return "ERROR"

    def __str__(self):
        return self.display()

    def __unicode__(self):
        return self.display()

    def __cmp__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Cannot compare Money object with {0} object".format(type(other)))
        if self.currency != other.currency:
            raise NotImplementedError("Cannot compare {0} with {1}".format(self.currency, other.currency))
        return self.amount - other.amount

    def __neg__(self):
        return Money(-self.amount, self.currency)

    def __pos__(self):
        return Money(+self.amount, self.currency)

    def __add__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Cannot process Money object with {0} object".format(type(other)))
        if self.currency != other.currency:
            raise NotImplementedError("Cannot process {0} with {1}".format(self.currency, other.currency))
        return Money(self.amount + other.amount, self.currency)

    def __sub__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Cannot process Money object with {0} object".format(type(other)))
        if self.currency != other.currency:
            raise NotImplementedError("Cannot process {0} with {1}".format(self.currency, other.currency))
        return Money(self.amount - other.amount, self.currency)

    def __mul__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Cannot process Money object with {0} object".format(type(other)))
        if self.currency != other.currency:
            raise NotImplementedError("Cannot process {0} with {1}".format(self.currency, other.currency))
        return Money(self.amount * other.amount, self.currency)

    def __div__(self, other):
        if not isinstance(other, Money):
            raise TypeError("Cannot process Money object with {0} object".format(type(other)))
        if self.currency != other.currency:
            raise NotImplementedError("Cannot process {0} with {1}".format(self.currency, other.currency))
        return Money(self.amount / other.amount, self.currency)

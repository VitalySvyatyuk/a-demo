# coding: utf-8

import re
import decimal
from django.utils.translation import ugettext_lazy as _, get_language
from django.utils.numberformat import format


def round_floor(value, precision=2):
    """Convert to Decimal and round_floor to precision numbers after the
    floating point.

    This is a workaround for values displaying bigger then they are when
    printed through "%.2f" % value

    >>> round_floor(16.09, 2)
    Decimal('16.09')
    >>> round_floor(16.899, 2)
    Decimal('16.89')
    """
    if isinstance(value, float):
        value = (('%%.%sf' % (precision + 2)) % value)[:len(('%%.%sf' % precision) % value)]
    return decimal.Decimal(value)


def decimal_round(n, precision=2):
    return decimal.Decimal(n).quantize(decimal.Decimal(pow(decimal.Decimal("0.1"), precision)))


# the only way to make property for classmethod
class CurrencyMetaClass(type):
    @property
    def all_currencies(cls):
        return cls.register.values()

    @property
    def valute_currencies(cls):
        return [v for v in cls.register.values() if not v.is_metal]

    @property
    def metal_currencies(cls):
        return [v for v in cls.register.values() if v.is_metal]


class Currency(object):
    __metaclass__ = CurrencyMetaClass

    register = {}

    def __init__(self, slug, **kwargs):
        self.slug = slug
        self.__dict__.update(kwargs)
        if 'verbose_name' not in kwargs:
            self.verbose_name = self.slug
        if 'group_regex' not in kwargs:
            self.group_regex = '_%s' % self.slug.lower()
        if 'instrument_name' not in kwargs:
            self.instrument_name = self.slug
        if 'symbol' not in kwargs:
            self.symbol = self.slug

        self.group_regex = re.compile(self.group_regex)

        self.__class__.register[self.slug] = self

    def __str__(self):
        return self.slug

    def __repr__(self):
        return '<Currency: %s>' % self.slug

    def __unicode__(self):
        return unicode(self.verbose_name)

    def display_amount(self, amount=111, precision=2, with_slug=None):
        amount = decimal_round(amount, precision)
        amount_str = format(amount, '.', grouping=3, thousand_sep=' ', force_grouping=True)

        slug = self.symbol if with_slug is None else with_slug

        if get_language() == 'ru':
            return u'%s %s' % (amount_str, slug)

        if amount < 0:
            return amount_str.replace('-', u'-%s' % slug)

        return u'%s %s' % (slug, amount_str)


def choices(*currencies):
    """Generate a choices list

    If currencies list is provided, use only them.
    The list can contain strings or Currency instances
    """
    result = []
    currencies = currencies or (c for name, c in Currency.register.iteritems() if name != "RUB")
    for currency in currencies:
        currency = get_currency(currency)
        result.append((currency.slug, currency.slug))
    return result


USD = Currency(
    slug='USD',
    group_regex='_us',
    symbol=u'$',
    verbose_name=_('US Dollar'),
    is_metal=False,
)

RUR = Currency(
    slug='RUR',
    group_regex='_ru',
    instrument_name='RUB',
    verbose_name=_('Russian rouble'),
    is_metal=False,
)

# Alias
Currency.register['RUB'] = RUR
RUB = RUR

# EUR = Currency(
#     slug='EUR',
#     group_regex='_eu',
#     symbol=u'€',
#     verbose_name=_("Euro"),
#     is_metal=False,
# )

# GOLD = Currency(
#     slug='GOLD',
#     instrument_name='XAU',
#     group_regex='_gold',
#     verbose_name=_("Gold"),
#     is_metal=True,
#     index=1,
# )
#
# SILVER = Currency(
#     slug='SILVER',
#     instrument_name='XAG',
#     group_regex='_silv',
#     verbose_name=_("Silver"),
#     is_metal=True,
#     index=2,
# )
#
# # Shortcut for compatibility with older code
# SILV = SILVER
#
# PLT = Currency(
#     slug='PLT',
#     group_regex='_plt',
#     verbose_name=_("Platinum"),
#     is_metal=True,
#     index=3,
# )
#
# PAL = Currency(
#     slug='PAL',
#     group_regex='_pal|_palad',
#     verbose_name=_("Palladium"),
#     is_metal=True,
#     index=4,
# )
#
# UAH = Currency(
#     slug='UAH',
#     group_regex='_uah',
#     symbol=_("UAH symbol"),
#     verbose_name=_("Ukrainian hryvnia"),
#     is_metal=False,
# )
#
# GBP = Currency(
#     slug='GBP',
#     verbose_name=_("Great Britain Pound"),
#     symbol=u'£',
#     is_metal=False,
# )
#
# CHF = Currency(
#     slug='CHF',
#     verbose_name=_('Swiss franc'),
#     is_metal=False,
# )
#
# JPY = Currency(
#     slug='JPY',
#     symbol=u'¥',
#     verbose_name=_('Japanese yen'),
#     is_metal=False,
# )
#
# IDR = Currency(
#     slug='IDR',
#     symbol=u'Rp',
#     verbose_name=_('Indonesian rupiah'),
#     is_metal=False,
# )
#
# CNY = Currency(
#     slug='CNY',
#     verbose_name=_('Chinese yuan'),
#     is_metal=False,
# )
#
# BTC = Currency(
#     slug='BTC',
#     verbose_name=_('Bitcoin'),
#     is_metal=False
# )


def get_currency(name, create=False):
    if isinstance(name, Currency):
        return name
    currency = Currency.register.get(name)
    if currency:
        return currency
    if create:
        return Currency(name)


def get_by_group(group):
    if not group:
        return
    for currency in Currency.register.itervalues():
        if currency.group_regex.search(group):
            return currency

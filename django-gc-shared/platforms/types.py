# -*- coding: utf-8 -*-
"""
Module provides available trading account types with properties.
"""
import re
from operator import or_

from django.utils.datastructures import MergeDict
from django.utils.encoding import force_unicode, smart_str
from django.utils.functional import curry
from django.utils.translation import ugettext_lazy as _
from currencies import currencies

from shared.werkzeug_utils import cached_property, import_string

HAS_NO_OPTIONS = 0
HAS_EXECUTION_OPTIONS = 1
HAS_CURRENCY_OPTIONS = 2
HAS_BINARY_OPTIONS_TYPE_OPTIONS = 4
MARKET_EXECUTION = 'market'
INSTANT_EXECUTION = 'instant'
AMERICAN_OPTIONS = 'american'
EUROPEAN_OPTIONS = 'european'


def get_account_types():
    """Function returns a dict of all available account types."""
    return AccountType.register


def get_account_type(group):
    """
    Function returns account type for a given group string, which
    should either match account type's slug or regex value.
    """
    for account_type in AccountType.register.itervalues():
        if group in account_type or group == account_type.slug:
            return account_type


class AccountType(object):
    """
    Available trading account type.
    """
    register = {}  # type: ignore

    def __init__(self, **attrs):
        # Compiling group regex ...
        if not "regex" in attrs:
            # warn("Account type doesn't declare group regex, using slug value.")
            attrs["regex"] = "^%s$" % attrs['slug']
        attrs["regex"] = re.compile(attrs["regex"])

        # ... and assigning default values.
        defaults = {"login_required": False,
                    "_account_form": "platforms.mt4.forms.Mt4AccountForm",
                    "_profile_form": "profiles.forms.BriefProfileForm",
                    "agreements": ['client_agreement', 'risk_disclosure', 'order_execution_policy'],
                    "notification_name": "account_created",
                    "group_choices": {},
                    "available_options": HAS_NO_OPTIONS,
                    "can_change_leverage": False,
                    'engine': 'default',
                    'is_ib_account': False,
                    'min_deposit': 0,
                    'max_per_user': 5,  # How many active accounts of this type can a single user have
                    'no_inout': False,  # In/Out operations for this account should be disabled
                    'creation_callback': None,  # Allows to specify a callback function executed after account creation
                    "leverage_choices": (100, 75, 66, 50, 33, 25, 20, 15, 10, 5, 3, 2, 1)}
        defaults.update(  # Note: the rest default to None.
            dict.fromkeys(["deposit", "group", "leverage_default"]))

        for attr, value in MergeDict(attrs, defaults).iteritems():
            setattr(self, attr, value)

        self.__class__.register[self.slug] = self

    def __repr__(self):
        return smart_str("<AccountType: %s>" % self.name)

    def __str__(self):
        return force_unicode(self).encode("utf-8")

    def __unicode__(self):
        return force_unicode(self.name)

    def __eq__(self, other):
        """Checks if account type is equal to another account type.

        Which is True, when their id's are equal, or when they have
        equal slug values and False otherwise.
        """
        try:
            return id(self) == id(other) or self.slug == other.slug
        except AttributeError:
            return False

    def __contains__(self, group):
        """Checks if account type includes accounts of a given group.

        It evaluates to True if a given group is a string, and it matches
        account type's regex and False otherwise.
        """
        if isinstance(group, basestring):
            return self.regex.match(group)
        else:
            return False

    def __or__(self, other):
        if isinstance(other, basestring):
            return '|'.join((self.regex.pattern, other))
        if not isinstance(other, AccountType):
            raise TypeError('Unsupported operand type for |. Only AccountType | AccountType is supported.')
        return '|'.join((self.regex.pattern, other.regex.pattern))

    def __ror__(self, other):
        return self.__or__(other)

    @cached_property
    def profile_form(self):
        return import_string(self._profile_form)

    @cached_property
    def account_form(self):
        return curry(import_string(self._account_form),
                     account_type=self)

    @property
    def is_demo(self):
        return self.engine == 'demo'


# Real trading account - mt4 by default
StandardAccountType = AccountType(
    slug='ARM_MT4_Live',
    name=u'ECN.MT',
    can_change_leverage=True,
    leverage_default=50,
    min_deposit=500,

    # notification_name="realstandard_created",
)

DemoStandardAccountType = AccountType(
    slug='demoARM',
    name=u'ECN.MT',
    leverage_default=50,
    deposit=10000,
    engine='demo',
    max_per_user=20,
    # notification_name="demostandard_created",
)


RealMicroAccountType = AccountType(
    slug="realmicro",
    regex="^<disabled>$",
)


RealIBAccountType = AccountType(
    slug='ARM_MT4_Agents',
    name='Partner',
    leverage_default=1,
    leverage_choices=(1, ),
    is_ib_account=True,
    agreements=['real_ib_partner'],
    _account_form='platforms.mt4.forms.Mt4RealIBForm',
    max_per_user=1,
)


def demo_regex():
    """Build a regex of demo account types"""
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues() if a.deposit) or "a^"  # a^ will never match anything


def real_regex():
    """Build a regex of real account types"""
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues() if not a.deposit) or "a^"


def real_not_partner_regex():
    """Build a regex of real account types excluding IBs"""
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues() if not a.deposit and not a.is_ib_account) or "a^"


def not_partner_regex():
    """Build a regex of real account types excluding IBs"""
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues() if not a.is_ib_account) or "a^"


def get_groups_regex(slugs):
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues()
                    if a.slug.lower() in slugs) or "a^"


def micro_regex():
    """Build a regex of micro account types"""
    return '|'.join(a.regex.pattern for a in AccountType.register.itervalues()
                    if 'micro' in a.slug.lower()) or "a^"


# fx = Std +M
def real_accounts_for_forex_regex():
    """Build a regex of real types of standard, micro, swapfree and ecn"""
    return get_groups_regex(['realstandard']) or "a^"


def read_only_slugs():
    # Счета, на которых нет торговли
    return []


def read_only_slugs_oncreate():
    # на счёта типа LammMasterAccountType торговля возможно после пополнения суммы, которую он указал в base_capital.
    # При создании такого счёт, задаём ему изначально read_only=1 (MT4)
    slugs = read_only_slugs()
    return slugs


SSStandardAccountType = AccountType(
    _account_form='platforms.strategy_store.forms.SSAccountForm',
    slug='realstandard_ss',
    name=u"ECN.Invest",
    can_change_leverage=True,
    leverage_choices=[],
    min_deposit=100,
    max_per_user=1,
    # notification_name="realstandard_created",
)


SSDemoStandardAccountType = AccountType(
    _account_form='platforms.strategy_store.forms.SSAccountForm',
    slug='demostandard_ss',
    name=u"ECN.Invest",
    leverage_choices=[],
    deposit=10000,
    max_per_user=1,
    can_be_used_as_pamm_investor=True,
    engine='demo',
    # notification_name="demostandard_created",
)


CFHStandardAccountType = AccountType(
    _account_form='platforms.cfh.forms.CFHAccountForm',
    slug='realstandard_cfh',
    name=u"ECN.PRO",
    can_change_leverage=True,
    leverage_choices=[100, 75, 50, 33, 25, 20, 10, 5, 1],
    leverage_default=50,
    min_deposit=1000,
    # notification_name="realstandard_cfh_created",
)


CFHDemoStandardAccountType = AccountType(
    _account_form='platforms.cfh.forms.CFHAccountForm',
    slug='demostandard_cfh',
    name=u"ECN.PRO",
    leverage_choices=[100, 75, 50, 33, 25, 20, 10, 5, 1],
    leverage_default=50,
    deposit=10000,
    can_be_used_as_pamm_investor=True,
    engine='demo',
    max_per_user=20,
    # notification_name="demostandard_cfh_created",
)

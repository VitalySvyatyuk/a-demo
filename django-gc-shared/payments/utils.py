# -*- coding: utf-8 -*-
from copy import deepcopy

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.http import Http404
from django.template.loader import get_template, TemplateDoesNotExist
from django.utils.encoding import force_unicode
from django.utils.importlib import import_module
from django.utils.translation import get_language
from django.conf import settings

from payments.__init__ import PAYMENT_SYSTEMS_REVERSED, PAYMENT_SYSTEM_TYPES
from shared.datastructures import Bunch
from shared.werkzeug_utils import cached_property


def get_account_requests_stats(account=None):
    from collections import defaultdict
    from datetime import datetime, timedelta
    from payments.models import DepositRequest
    from platforms.models import TradingAccount
    from platforms.converter import convert_currency

    if account.is_ib:
        agents = account.agent_clients.values_list("login", flat=True)
        accounts_list = TradingAccount.objects.filter(mt4_id__in=list(agents))
    else:
        accounts_list = account.user.accounts.all()

    stats = defaultdict(float)
    systems = {}
    for acc in accounts_list:
        x = [(x.payment_system, x.amount, x.currency)
             for x in DepositRequest.objects.filter(account=acc, is_committed=True)]

        for system, amount, currency in x:
            if isinstance(system, basestring):
                system = load_payment_system("payments.system.%s" % system)
                if system is None:
                    continue

            sys_name = unicode(system)
            stats[sys_name] += float(convert_currency(amount=amount, from_currency=currency, to_currency="USD",
                                                      for_date=datetime.today()-timedelta(2))[0])
            if sys_name not in systems:
                systems[sys_name] = system

    summ = sum(stats.values())
    res = []

    for system in stats:
        percent = int(stats[system]/summ*100) if summ > 0 else 0
        res.append((systems[system], round(stats[system], 2), percent))

    return res

# A list of options payment system might define.
#
#  attribute                | req? | description
# --------------------------+------+------------------------------------------------------
#  name                     | yes  | payment system title, used in templates
#  slug                     | yes  | payment system unique identifier, used internally
#  logo                     | yes  | payment system logo icon, should point to a file in
#                           |      | MEDIA_URL/images/payment_systems/ directory
#  list                     | no   | an optional boolean flag, if false, a payment system
#                           |      | isn't rendered in deposit / withdraw lists
#  languages                | no   | defines for which language display payment system
#  currency                 | no   | force currency for this payment system, which means
#                           |      | no currency select will be displayed on both deposit
#                           |      | and withdraw forms
#  purse_regex              | no   | a regular expression for validating purse values,
#                           |      | nice but definitely not required
#  purse_example            | no   | a string, rendered as help_text on each form with a
#                           |      | purse field on it
#  mt4_payment_slug         | no   | used for default scheme of comments at MT4
#                           |      | ({mt4_payment_slug}[request_id])
#  has_deposit_commission   | no   | whether the system has commission for deposit
#  with_purse_only          | no   | shows if requisit contains only purse
# ----------------------------------------------------------------------------------------

_OPTION_NAMES = (
    "currencies", "name", "slug", "logo", "list", "purse_example", "purse_regex",
    "DetailsForm", "DepositForm", "WithdrawForm", "languages", "countries",
    "mt4_payment_slug",
    "has_deposit_commission", "transfer_details", "time_to_deposit",
    "with_purse_only", "templates"
)


def memoize_load(load):
    payment_systems_cache = {}

    def inner(path, *args, **kwargs):

        if isinstance(path, PaymentSystemProxy):
            return path

        # обобщение на случаи, если платежная система
        # названа "bankrur" или "payments.systems.bankrur"
        name = path.rsplit(".")[-1]

        # Credit card aliases shouldn't be cached because they may change for every request
        if name not in payment_systems_cache or name in CREDIT_CARD_ALIASES:
            payment_systems_cache[name] = load(name, *args, **kwargs)

        return payment_systems_cache[name]

    return inner


CREDIT_CARD_ALIASES = {
    "mastercard": "Mastercard",
    "visa": "Visa",
}

# Not moving this to settings, because it can change a bit too often and depends on the nearby code
ENABLED_CARD_SYSTEMS = ()


def get_latest_credit_card_success(user):
    from payments.models import DepositRequest
    ps_query = Q()  # payment_system field doesn't support __in queries
    for ps in ENABLED_CARD_SYSTEMS:
        ps_query |= Q(payment_system=ps)

    latest_success = DepositRequest.objects.filter(ps_query, account__user=user, is_committed=True) \
        .order_by('-creation_ts').first()
    if latest_success:
        return latest_success.payment_system.slug


def get_failing_credit_card_processings(user, allowed_card_systems=ENABLED_CARD_SYSTEMS):
    from payments.models import DepositRequest
    failing_pses = DepositRequest.objects.filter(account__user=user)\
                                 .exclude(payment_system__in=DepositRequest.objects.filter(
                                                                account__user=user,
                                                                is_committed=True
                                                            ).values('payment_system'))\
                                 .order_by('payment_system')\
                                 .distinct('payment_system')\
                                 .values_list('payment_system', flat=True)
    result = set(failing_pses) & set(allowed_card_systems)
    if len(result) == len(allowed_card_systems):  # If all the systems have failed, pretend nothing happened
        return set()
    return result


def get_best_credit_card_processing(request):
    failing_processings = set()

    return ""


@memoize_load
def load_payment_system(path, raise_404=False, request=None):
    override_name = False
    if path in CREDIT_CARD_ALIASES:
        override_name = CREDIT_CARD_ALIASES[path]
        path = get_best_credit_card_processing(request)

    if path not in PAYMENT_SYSTEMS_REVERSED:
        if raise_404:
            raise Http404()
        return

    try:
        module = import_module("payments.systems." + path)
    except (ImportError, ValueError) as exc:
        if raise_404:
            raise Http404()
        raise ImproperlyConfigured("Error importing payment system %s: %s '%s'" % (path, type(exc), exc))

    for option in ("name", "slug", "logo"):
        if not hasattr(module, option):
            raise ImproperlyConfigured("Payment system %r is missing an option: %s" % (module, option))

    psp = PaymentSystemProxy(module)
    if override_name:
        psp.name = override_name
    return psp


def get_payment_systems():
    lang = get_language()
    payment_systems = deepcopy(PAYMENT_SYSTEM_TYPES)
    # payment_systems['deposit']['card']['systems'] = ['visa', 'mastercard']

    for op, op_data in payment_systems.items():
        for psgroup, psgroup_data in op_data.items():
            loaded_systems = [
                (sys_name, load_payment_system(sys_name))
                for sys_name in psgroup_data["systems"]
            ]
            psgroup_data["systems"] = {
                sys_name: sys
                for sys_name, sys in loaded_systems
                if sys.visible and (lang in getattr(sys, "languages", []) or not hasattr(sys, "languages"))
            }
    return payment_systems


def build_absolute_uri(request, url):
    return request.build_absolute_uri(url)


class PaymentSystemProxy(Bunch):
    """
    A dict wrapper around payment system module.

    We're forced to convert a module object to a dot accessible
    dict, because neither modules nor dynamically created classes
    can be pickled (at least out of the box).
    """
    def __init__(self, module):
        super(PaymentSystemProxy, self).__init__(
            (attr, getattr(module, attr))
            for attr in dir(module)
            if attr in _OPTION_NAMES
        )

    def __str__(self):
        return self.name.encode("utf-8")

    def __eq__(self, other):
        if isinstance(other, PaymentSystemProxy):
            return self.slug == other.slug
        elif isinstance(other, basestring):
            return self.slug == other

        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __unicode__(self):
        return force_unicode(self.name)

    __repr__ = __str__

    @cached_property
    def deposit_description_template(self):
        try:
            template = "payments/descriptions/%s/deposit.html" % self.slug
            get_template(template)
        except TemplateDoesNotExist:
            return

        return template

    @cached_property
    def withdraw_description_template(self):
        try:
            template = "payments/descriptions/%s/withdraw.haml" % self.slug
            get_template(template)
        except TemplateDoesNotExist:
            pass
        else:
            return template

    @property
    def deposit_redirect(self):
        return getattr(self.DepositForm, "action", None)

    @property
    def visible(self):
        return getattr(self, "list", True)

    def get_form(self, operation):
        """Returns a form class for a given operation."""
        return getattr(self, operation.title() + "Form")

    def is_auto(self, operation):
        """Returns True if a given operation can be executed automatically."""
        return bool(getattr(self.get_form(operation), "action", None))

    def is_auto_deposit(self):
        """Returns True if a 'deposit' operation can be executed automatically."""
        return self.is_auto("deposit")

    # FIXME(Sergei): remove the latter after we migrate to a sane templating
    # engine.
    is_auto_deposit = property(lambda self: self.is_auto("deposit"))
    is_auto_withdraw = property(lambda self: self.is_auto("withdraw"))


@receiver(post_migrate)
def create_permissions(sender, **kwargs):
    if sender.label != 'payments':
        return
    from models import DepositRequest
    
    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(DepositRequest),
        codename="can_commit_payments")

    if created:
        permission.name = "Can pay on MT4"
        permission.save()
        print "Adding permission: %s" % permission

    permission, created = Permission.objects.get_or_create(
        content_type=ContentType.objects.get_for_model(DepositRequest),
        codename="can_deposit_webmoney_on_any_account")

    if created:
        permission.name = "Can zakidyvat on any Webmoney account"
        permission.save()
        print "Adding permission: %s" % permission


class PaymentException(Exception):
    pass

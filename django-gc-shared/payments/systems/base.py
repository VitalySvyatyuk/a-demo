# -*- coding: utf-8 -*-
import inspect
import os
from collections import namedtuple
from decimal import Decimal

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.db import transaction
from django.db.models import Q
from django.db.models.query import QuerySet
from django.forms import ModelChoiceField
from django.shortcuts import redirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies import currencies
from geobase.models import Country
from geobase.phone_code_widget import CountryPhoneCodeFormField
from log.models import Logger, Events
from payments.models import UserRequisit, DepositRequest, WithdrawRequest, WithdrawRequestsGroup
from payments.utils import PaymentSystemProxy, load_payment_system
from platforms.converter import convert_currency
from platforms.models import TradingAccount
from shared.translify import translify
from shared.werkzeug_utils import cached_property

CommissionCalculationResult = namedtuple(
    "CommissionCalculationResult",
    [
        # сумма заявки, сконвертированная в валюту платежной системы
        "amount",
        # комиссия, в валюте платежной системы
        "commission",
        # валюта, в которой оперирует платежная система
        "currency"
    ]
)


class BaseForm(forms.ModelForm):
    """
    Base class for payment forms.
    """
    action, auto = None, False
    method = "POST"

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        account = kwargs.pop("account", None) or self.request.GET.get("account")
        self.requisit = kwargs.pop("requisit", None) or self.request.GET.get("requisit")

        if not hasattr(self, "payment_system"):
            self.payment_system = kwargs.pop("payment_system", None)

        super(BaseForm, self).__init__(
            *args, **dict(kwargs, auto_id="%s-%%s" % self.payment_system.slug))

        # Loading account obj
        if account:
            try:
                account = self.request.user.accounts.get(mt4_id=int(account))
            except (TradingAccount.DoesNotExist, TypeError):
                self.account = None
            else:
                self.account = account
                self.fields["account"].initial = account
        else:
            self.account = None

        # Available currencies
        self.fields["currency"].choices = currencies.choices(*self.payment_system.currencies)
        self.auto_id = "id_%s"

    def clean_account(self):
        """
        Validate account object.
        """
        account = self.cleaned_data.get("account")

        if not isinstance(account, TradingAccount):

            # если юзер - агент, который может закидывать на любой счет через вебмани,
            # то для него не нужно проверять, что счет ему принадлежит
            if self.request.user.has_perm("payments.can_deposit_webmoney_on_any_account") \
                    and self.payment_system.slug == "webmoney":
                kwargs = {}
            else:
                kwargs = {"user": self.request.user}

            if isinstance(account, (int, long)):
                accounts = TradingAccount.objects.filter(Q(id=account) | Q(mt4_id=account),
                                                     **kwargs)
            elif isinstance(account, basestring):
                accounts = TradingAccount.objects.filter(Q(id=int(account)) | Q(mt4_id=int(account)),
                                                     **kwargs)
            else:
                raise TypeError(_("Unknown type of account field"))

            if accounts:
                account = accounts[0]
            else:
                raise ValidationError(_("Account does not exist"))

        if account.is_demo:
            raise forms.ValidationError(_("Can't operate on a demo account."))

        if account.no_inout:
            raise forms.ValidationError(_("Deposit/withdrawal operations are unavailable for this account type."))

        return account

    @transaction.atomic
    def save(self, **kwargs):
        """
        Save model to DB.
        """
        instance = super(BaseForm, self).save(commit=False)
        instance.payment_system = self.payment_system
        instance.user = self.request.user

        instance.params = dict(
            (key, value)
            for key, value in self.cleaned_data.iteritems()
            if not hasattr(instance, key) and key not in ["requisit_id", "requisit",
                                                          "ps", "ps_type"]
        )
        instance.params['domain'] = self.request.get_host()

        if hasattr(self.payment_system, 'currency') and self.payment_system.currency:
            instance.currency = self.payment_system.currency

        if kwargs.get("commit", True):
            super(BaseForm, self).save()

        return instance

    def mutate(self):
        if not self["account"].is_hidden:
            # Making `account` a hidden field, so it wont be render in
            # the preview table.
            self.fields["account"].widget = \
                forms.HiddenInput(attrs={"value": self["account"].data})

        return self

    @cached_property
    def payment_system(self):
        """Reference to the payment system module, which contains this form."""
        return PaymentSystemProxy(inspect.getmodule(self.__class__))

    @classmethod
    def verify(cls, object):
        """Checks if a given object is allowed for execution."""
        return False

    @classmethod
    def execute(cls, request, instance):
        """Does w\e with a given instance and returns an HttpRequest."""
        return redirect("mt4_account_list")

    @property
    def logo_url(self):
        if self.logo:
            return os.path.join(settings.STATIC_URL, 'img', 'payment_systems', self.logo, )

    @classmethod
    def generate_mt4_comment(cls, payment_request):
        ps = inspect.getmodule(cls)
        if not hasattr(ps, "mt4_payment_slug"):
            raise NotImplementedError("Payment systems must either specify 'mt4_payment_slug' or"
                                      " override generate_mt4_comment method on its forms")
        return "{%s}[%s]" % (ps.mt4_payment_slug, payment_request.id)

    @classmethod
    def generate_mt4_request_id(cls, payment_request):
        return str(payment_request.id)


class DepositForm(BaseForm):

    # Override this and set (AMOUNT, CURRENCY) if needed
    MAX_AMOUNT = None
    MIN_AMOUNT = None

    templates = ["payments/_form_with_errors.html"]

    currency = forms.ChoiceField(label=_('Currency'), help_text=_("Choose currency"))

    amount = forms.DecimalField(label=_("Amount"), help_text=string_concat(
        _("Amount of money to deposit."), " ",
        _("Attention! Specify amount on your account after deduction of the system's charge"))
    )

    commission_rate = Decimal(0)

    class Meta:
        model = DepositRequest
        fields = ("account", "purse", "currency", "amount", )

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        if hasattr(self.payment_system, "purse_regex"):
            self.fields["purse"].help_text = _("Your %(payment_system)s purse, e.g. %(example)s") % {
                'payment_system': unicode(self.payment_system.name),
                'example': self.payment_system.purse_example
            }

        self.fields["account"].queryset = (
            self.request.user.accounts.alive().non_demo()
            if self.request else QuerySet().none()
        )

        if (not self.payment_system.slug == "webmoney" or
                not self.request.user.has_perm("payments.can_deposit_webmoney_on_any_account")):
            assert self.fields["account"].queryset.exists()

    def clean_purse(self):
        """
        Purse number validation.
        """
        purse = self.cleaned_data["purse"]

        if hasattr(self.payment_system, "purse_regex"):
            # валидация регулярки для кошелька
            # сделано не через валидаторы, потому что валидатор меняет текст ошибки на свой стандартный :(
            RegexValidator(
                self.payment_system.purse_regex,
                message=_("Wrong %s purse number.") % unicode(self.payment_system.name)
            )(purse)

        return purse

    def clean(self):
        """
        Validate deposit request.
        """

        account = (self.cleaned_data["account"])
        if not DepositRequest.objects.filter(account=account, is_committed=True).exists():
            if self.MAX_AMOUNT and "amount" in self.cleaned_data and "currency" in self.cleaned_data:
                amount = self.cleaned_data["amount"]
                currency = self.cleaned_data["currency"]
                max_amount, max_amount_currency = self.MAX_AMOUNT
                converted_max_amount = convert_currency(max_amount, max_amount_currency, currency)
                if converted_max_amount[0] < amount:
                    self._errors["amount"] = [
                        _("You cant deposit more than %(amount)s with %(system)s") % {
                            "amount": converted_max_amount[1].display_amount(converted_max_amount[0]),
                            "system": self.payment_system.name
                        }
                    ]

            if self.MIN_AMOUNT and "amount" in self.cleaned_data and "currency" in self.cleaned_data:
                amount = self.cleaned_data["amount"]
                currency = self.cleaned_data["currency"]
                min_amount, min_amount_currency = self.MIN_AMOUNT
                converted_min_amount = convert_currency(min_amount, min_amount_currency, currency)
                if converted_min_amount[0] > amount:
                    self._errors["amount"] = [
                        _("You cant deposit less than %(amount)s with %(system)s") % {
                            "amount": converted_min_amount[1].display_amount(converted_min_amount[0]),
                            "system": self.payment_system.name
                        }
                    ]

        cleaned_amount = self.cleaned_data.get("amount")
        cleaned_account = self.cleaned_data.get("account")
        cleaned_currency = self.cleaned_data.get("currency")

        if cleaned_amount is not None and cleaned_account and cleaned_currency:
            cleaned_amount = float(cleaned_amount)

            if cleaned_amount <= 0:
                self._errors["amount"] = [_('Wrong amount')]

            if cleaned_account.group.min_deposit:  # If minimum deposit is defined for the account
                to_currency = currencies.get_currency(cleaned_currency)
                account_balance = cleaned_account.get_balance(currency=to_currency, with_bonus=True)[0]
                if account_balance is not None:
                    min_deposit = convert_currency(cleaned_account.group.min_deposit, 'USD', to_currency)[0]

                    if not self.request.user.is_superuser and account_balance < min_deposit:
                        min_deposit_amount = min_deposit - account_balance
                        if cleaned_amount < min_deposit_amount:
                            self._errors["amount"] = [_('Minimum deposit amount is %(amount)s %(currency)s') %
                                                      {'amount': str(round(min_deposit_amount)),
                                                       'currency': str(to_currency)}]

                else:
                    self._errors["account"] = [_('Cannot determine the account balance. Try again later or contact support')]

        return super(DepositForm, self).clean()

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

    @classmethod
    def calculate_commission(cls, request, full_commission=False):
        return cls._calculate_commission(request)

    def save(self, **kwargs):
        res = super(DepositForm, self).save(**kwargs)

        Logger(user=self.request.user, ip=self.request.META["REMOTE_ADDR"],
               event=Events.DEPOSIT_REQUEST_CREATED, content_object=res).save()

        return res

    @classmethod
    def is_automatic(cls, instance):
        return cls.auto

    def render_form(self):
        template = self.payment_system.templates.get('deposit', "payments/_form_with_errors.html")
        return render_to_string(
            template, RequestContext(self.request, {
                'form': self,
                "ps": self.payment_system,
                "details": self.payment_system.transfer_details['deposit'],
                "PAYMENTS_RECEIVER": settings.PAYMENTS_RECEIVER
            }))


class PhonePursePaymentForm(forms.BaseForm):
    def __init__(self, *args, **kwargs):
        super(PhonePursePaymentForm, self).__init__(*args, **kwargs)

        label = self.fields["purse"].label
        help_text = self.fields["purse"].help_text

        self.fields["purse"] = CountryPhoneCodeFormField(label=label, help_text=help_text)


class DetailsForm(forms.ModelForm):

    purse = forms.CharField(label=_("Purse"))

    class Meta:
        # actually UserRequisit has not been used
        # HACK, just to make Django work with mixins below
        model = UserRequisit
        fields = ("purse",)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.payment_system = load_payment_system(kwargs.pop("payment_system"))

        super(DetailsForm, self).__init__(*args, **kwargs)

        self.auto_id = "id_%s"

        if hasattr(self.payment_system, "purse_regex"):
            self.fields["purse"].help_text = _("Your %(payment_system)s purse, e.g. %(example)s") % {
                'payment_system': unicode(self.payment_system.name),
                'example': self.payment_system.purse_example
            }

    def clean_purse(self):
        purse = self.cleaned_data["purse"]

        if hasattr(self.payment_system, "purse_regex"):
            # валидация регулярки для кошелька
            # сделано не через валидаторы, потому что валидатор меняет текст ошибки на свой стандартный :(
            RegexValidator(
                self.payment_system.purse_regex,
                message=_("Wrong %s purse number.") % unicode(self.payment_system.name)
            )(purse)

        return purse

    def save(self):
        return dict(self.cleaned_data)


class WithdrawForm(BaseForm):

    # Override this and set (AMOUNT, CURRENCY) if needed
    MIN_AMOUNT = None

    commission_rate = Decimal(0)

    class Meta:
        model = WithdrawRequest
        fields = ("account", "currency", "amount", "reason")

    def _get_min_amount(self, account):
        return self.MIN_AMOUNT

    def __init__(self, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)

        self.fields["account"].queryset = self.request.user.accounts.non_demo().alive()
        self.fields["amount"].help_text = _("Amount of money to withdraw")

    def get_purse_field_name(self):
        return "purse"

    @staticmethod
    def get_withdraw_limit_data(account, include_pending_requests=True):
        from currencies.money import Money
        withdraw_limit = Decimal(account.balance_money.amount)

        # subtract money which already waiting for output
        if include_pending_requests:
            # TODO: why the f I use last group here? Should we just take all requests?
            group = WithdrawRequestsGroup.objects.filter(account=account, is_closed=False).last()
            if group:
                withdraw_requests = group.requests.filter(is_committed=None)
                if withdraw_requests:
                    withdraw_requests_amount = 0
                    for withdraw_request in withdraw_requests:
                        withdraw_requests_amount += Decimal(withdraw_request.amount_money.to(account.currency).amount)
                    withdraw_limit -= Decimal(withdraw_requests_amount)

        # Note: displaying a negative upper bound doesn't make sense,
        # so we round balance to zero in that case.
        withdraw_limit = max(0, withdraw_limit)

        # drop digits beyond needed precision
        withdraw_limit = currencies.round_floor(withdraw_limit)
        return Money(withdraw_limit, account.currency), Money(0, account.currency)

    def clean(self):

        for key in ('account', 'amount', 'currency'):
            if key not in self.cleaned_data:
                return self.cleaned_data
        account = self.cleaned_data["account"]

        if account.is_ib and not account.verification.exists():
            self._errors["account"] = [mark_safe(
                _('You should <a href="%(link)s" target="_blank">complete the verification process</a> '
                  'before withdrawing from account %(account)s') % {
                    'account': account.mt4_id,
                    'link': reverse("referral_verify_partner") + "?next=" + self.request.path
                }
            )]

        if account.is_disabled:
            self._errors["account"] = [_("You can't withdraw funds from this account")]

        # Allow withdrawals only to systems which had successful deposits or to bank
        if not (self.payment_system.slug in ("bankusd", "bankeur", "bankrur") or
                DepositRequest.objects.filter(payment_system=self.payment_system,
                                              account__user=account.user,
                                              is_committed=True).exists()):
            self._errors["account"] = [_("Please withdraw funds using the system which you used for deposit, or "
                                         "using wire transfer")]

        # для вебмани все конвертируем в валюту счета,
        # для остальных валюта выбирается в форме
        if self.payment_system.slug == "webmoney":
            to_currency = account.currency
        else:
            to_currency = currencies.get_currency(self.cleaned_data["currency"])

        amount = self.cleaned_data['amount']

        min_amount = self._get_min_amount(account)
        if min_amount:
            # получаем минимальное число средств в некоторой валюте
            min_amount, currency = min_amount
            # его нужно сконвертировать в валюту платежной системы
            min_amount, currency = convert_currency(min_amount, currency, to_currency, silent=False)

            if amount < min_amount:
                self._errors["amount"] = [_(
                    "Minimal amount of money you can withdraw "
                    "with this payment system is %(limit_value)s%(currency)s"
                ) % {
                    "limit_value": currencies.round_floor(min_amount),
                    "currency": currency.slug
                }]
        else:
            if not amount > 0:
                self._errors["amount"] = [_("Enter amount more than %s") % 0]

        try:
            withdraw_limit, bonuses = WithdrawForm.get_withdraw_limit_data(account)

            bonuses = bonuses.to(to_currency)

            if amount > withdraw_limit.amount:
                self._errors["amount"] = [_(
                    "Maximal amount of money you can withdraw for a chosen "
                    "account is %(limit_value)s%(currency)s ") % \
                                         {"limit_value": withdraw_limit.amount,
                                              "currency": withdraw_limit.currency.slug}]
        except:
            self._errors["account"] = [_('Cannot determine the account balance. Try again later or contact support')]
        # self.cleaned_data['last_transaction_id'] = 'sadfdsafsf'
        return self.cleaned_data

    @classmethod
    def is_automatic(cls, instance):
        return cls.auto

    @classmethod
    def _calculate_commission(cls, request):
        commission = request.amount * cls.commission_rate

        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

    @classmethod
    def calculate_commission(cls, request):
        return cls._calculate_commission(request)

    def save(self, *args, **kwargs):

        res = super(WithdrawForm, self).save(*args, **kwargs)
        last_deposit = DepositRequest.objects.filter(account=res.account).order_by('-creation_ts', )[0]
        res.last_transaction_id = last_deposit.transaction_id

        Logger(user=self.request.user, ip=self.request.META["REMOTE_ADDR"],
               event=Events.WITHDRAW_REQUEST_CREATED, content_object=res).save()

        return res

    def render_form(self, details_form):
        template = self.payment_system.templates.get('withdraw', "payments/_form_with_errors.html")
        return render_to_string(
            template, RequestContext(self.request, {
                'withdraw_form': self,
                'details_form': details_form,
                "ps": self.payment_system,
                "details": self.payment_system.transfer_details['withdraw'],
                "PAYMENTS_RECEIVER": settings.PAYMENTS_RECEIVER
            }))


class FormWithName(forms.ModelForm):

    name = forms.CharField(label=_("Your name"),
                           help_text=_("First, last and middle name (if any). Example: "
                                       "Andrei Ivanovich Denisov"))

    def __init__(self, *args, **kwargs):
        super(FormWithName, self).__init__(*args, **kwargs)

        # Populating user first and last name from User data.
        user = self.request.user

        last_name = user.last_name
        first_name = user.first_name
        middle_name = user.profile.middle_name

        if getattr(self, "name_format", None):
            msg = self.name_format
        else:
            msg = ""
            if last_name:
                msg += "%(last)s"
            if first_name:
                msg += (" " if msg else "") + "%(first)s"
            if middle_name:
                msg += (" " if msg else "") + "%(middle)s"

        self.fields["name"].initial = msg % {"last": last_name,
                                             "first": first_name,
                                             "middle": middle_name}

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if name != self.fields["name"].initial:
            raise ValidationError(_("You can't change the name here, "
                                    "if you need to change your profile name, please contact support"))
        return name


class FormWithTranslitedName(FormWithName):
    def __init__(self, *args, **kwargs):
        super(FormWithTranslitedName, self).__init__(*args, **kwargs)

        self.fields["name"].initial = translify(self.fields["name"].initial).title()
        self.fields["name"].help_text = _("First, last and middle name (if any) in latin transcription. "
                                          "Example: Andrei Ivanovich Denisov")


class FormWithTranslitedUppercaseName(FormWithTranslitedName):
    name = forms.CharField(label=_("Your name"),
                           help_text=_("Name, surname. You could use capital Latin letters, hyphen and spaces."
                                       " Example: ANDREI DENISOV"))
    name_format = "%(first)s %(last)s"

    def __init__(self, *args, **kwargs):
        super(FormWithTranslitedUppercaseName, self).__init__(*args, **kwargs)

        self.fields["name"].initial = self.fields["name"].initial.upper()



class FormWithCountry(forms.ModelForm):
    country = ModelChoiceField(label=_("Country"), help_text=_("The country where you live"),
                               queryset=Country.objects.all())

    def __init__(self, *args, **kwargs):
        super(FormWithCountry, self).__init__(*args, **kwargs)

        profile = self.request.user.profile
        self.fields["country"].initial = profile.country

    def clean_country(self):
        # HACK: unfortunately JSONField doesn't know how to handle
        # Django models, so we need to coerce Country into a string.
        return self.cleaned_data["country"].name


class FormWithCity(forms.ModelForm):
    city = forms.CharField(label=_('City'), max_length=100,
                           help_text=_('The city where you live'))

    def __init__(self, *args, **kwargs):
        super(FormWithCity, self).__init__(*args, **kwargs)

        profile = self.request.user.profile
        self.fields["city"].initial = profile.city

    def clean_city(self):
        # HACK: unfortunately JSONField doesn't know how to handle
        # Django models, so we need to coerce City into a string.
        return force_unicode(self.cleaned_data["city"])


# Helpers.
def make_hidden(value=None, choices=None):
    if choices is None:
        choices = ((value, value),)

    kwargs = {} if value is None else {"initial": value}

    return forms.ChoiceField(widget=forms.HiddenInput(attrs={"value": value}),
                             required=False, choices=choices, **kwargs)

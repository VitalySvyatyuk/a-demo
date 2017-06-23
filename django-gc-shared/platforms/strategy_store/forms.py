# -*- coding: utf-8 -*-
"""
Strategy Store account registration form.
"""
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Value, Func
# from django.conf import settings

from gcrm.models import Contact
from currencies import currencies
from payments.systems.base import make_hidden
from platforms.models import TradingAccount
from django.utils.translation import ugettext_lazy as _
from platforms.types import HAS_CURRENCY_OPTIONS, HAS_EXECUTION_OPTIONS, MARKET_EXECUTION, \
    get_account_type, read_only_slugs_oncreate
from platforms.forms import default_currencies_from_type, notification, execution_system_choices
from project.utils import get_accept_fields
from platforms.mt4 import calculate_available_leverages

GROUP_NAME_DEMO = 'demostandard_ss'
GROUP_NAME_REAL = 'realstandard_ss'


class SSAccountForm(forms.Form):
    leverage = forms.ChoiceField(label=_("Leverage"))
    deposit = forms.IntegerField(label=_("Initial deposit"), min_value=0,
                                 help_text=_("Available to demo accounts only."))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.account_type = kwargs.pop("account_type", None)
        super(SSAccountForm, self).__init__(*args, **kwargs)
        if not self.account_type:
            return

        if self.account_type.leverage_choices:
            available_leverages = calculate_available_leverages(
                group=self.account_type,
                user=self.request and self.request.user.is_authenticated() and self.request.user,
            )
            leverage_default = getattr(self.account_type, "leverage_default", None)
            if leverage_default not in available_leverages:
                leverage_default = available_leverages[0]
            leverage_choices = [(idx, '1:%i' % idx)
                                for idx in available_leverages]
            self.fields["leverage"].choices = leverage_choices
            self.fields["leverage"].initial = leverage_default
        else:
            del self.fields["leverage"]

        if self.account_type.available_options & HAS_EXECUTION_OPTIONS:
            self.fields["execution_system"] = forms.ChoiceField(
                label=_("Execution system"),
                choices=execution_system_choices(self.account_type),
                widget=forms.RadioSelect(),
                initial=MARKET_EXECUTION,
                required=False
            )

        if self.account_type.available_options & HAS_CURRENCY_OPTIONS:
            self.fields["currency"] = forms.ChoiceField(
                label=_("Currency"),
                initial=currencies.USD,
                choices=default_currencies_from_type(self.account_type),
                required=False,
            )

        # Initializing deposit fields, if account type requires deposit,
        # or removing it otherwise.
        if self.account_type.deposit is not None:
            self.fields["deposit"].initial = self.account_type.deposit
        else:
            del self.fields["deposit"]

        self.fields.update(get_accept_fields(self.request, self.account_type.agreements))

        self.fields["account_type"] = make_hidden(self.account_type.slug)

    def clean_currency(self):
        value = self.cleaned_data['currency']
        return currencies.get_currency(value)

    def clean(self):
        from platforms.views import CreateAccountView
        if CreateAccountView.max_accounts_reached(self.request.user, self.account_type):
            raise ValidationError("You have reached maximum number of allowed accounts of this type")
        self.cleaned_data["group"] = self.account_type.group

        return self.cleaned_data

    @transaction.atomic
    def save(self, profile=None):
        profile = profile or self.request.user.profile
        user = profile.user
        account = TradingAccount(platform_type='strategy_store', user=user, mt4_id=user.pk,
                                 group_name=GROUP_NAME_DEMO if self.account_type.is_demo else GROUP_NAME_REAL)
        password = account.api.account_create(account, initial_balance=self.cleaned_data.get('deposit', 0))
        account._login = user.email
        if password:
            account.save()
        Contact.objects.filter(user=user).exclude(tags__contains=['StrategyStore']).update(
            tags=Func(F('tags'), Value('StrategyStore'), function='array_append'))
        if self.account_type.is_demo:
            Contact.objects.filter(user=user).exclude(tags__contains=['demo']).update(
                tags=Func(F('tags'), Value('demo'), function='array_append'))
            notification.send([user], 'demo_invest_account_created',
                              {"password": password,
                               'type': self.account_type,
                               "account": account.mt4_id,
                               "login": user.email})

        else:
            Contact.objects.filter(user=user).exclude(tags__contains=['real']).update(
                tags=Func(F('tags'), Value('real'), function='array_append'))
            notification.send([user], 'real_invest_account_created',
                              {"password": password,
                               'type': self.account_type,
                               "account": account.mt4_id,
                               "login": user.email})
        return {"account": account, "password": password}

    save.async = False

    @classmethod
    def get_notification(cls):
        """ In order to be able to override in child form """
        return notification

    @classmethod
    def send_notification(cls, account, account_type_slug, **kwargs):
        """Send account creation email to account user"""

        account_type = get_account_type(account_type_slug)

        notification_data = {"account": account, "login": account.mt4_id, "group": account_type}
        kwargs.pop("group", None)
        notification_data.update(kwargs)

        recipients = [account.user]

        notification_name = None
        if getattr(cls, "notification_name", None):
            notification_name = cls.notification_name

        cls.get_notification().send(recipients, notification_name, notification_data,
                                    no_django_message=True)

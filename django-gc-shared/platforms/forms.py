# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, override

from currencies import *
from platforms.types import RealIBAccountType, StandardAccountType, DemoStandardAccountType
from platforms.utils import get_ip, create_password

from platforms.types import MARKET_EXECUTION, INSTANT_EXECUTION, HAS_BINARY_OPTIONS_TYPE_OPTIONS,\
    HAS_EXECUTION_OPTIONS, HAS_CURRENCY_OPTIONS, \
    AMERICAN_OPTIONS, EUROPEAN_OPTIONS,\
    get_account_type, read_only_slugs_oncreate
from notification import models as notification
from notification.models import get_notification_language
from payments.systems.base import make_hidden
from profiles.models import UserDocument
from project.utils import get_accept_fields


def default_currencies_from_type(account_type):
    try:
        return currencies.choices(*account_type.group_choices[MARKET_EXECUTION].viewkeys())
    except KeyError:
        raise NotImplementedError('Did not realised dynamic system for load currencies for chosen EXECUTION')


def execution_system_choices(account_type):
    result = []
    if account_type.group_choices.has_key(MARKET_EXECUTION):
        result.append((MARKET_EXECUTION, _('Market execution')))
    if account_type.group_choices.has_key(INSTANT_EXECUTION):
        result.append((INSTANT_EXECUTION, _('Instant execution')))
    return tuple(result)


EXECUTION_SYSTEM_CHOICES = (
    (MARKET_EXECUTION, _('Market execution')),
    (INSTANT_EXECUTION, _('Instant execution')),
)

BINARY_OPTIONS_TYPE_CHOICES = (
    (AMERICAN_OPTIONS, _('American-style options')),
    (EUROPEAN_OPTIONS, _('European-style options')),
)


class ChangeLeverageForm(forms.Form):
    leverage = forms.ChoiceField(label=_("The following leverage settings are "
                                         "available for the current balance of your account:"), required=True)

    notification_name = "leverage_change"

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        leverage_choices = self.account.get_available_leverages()

        max_leverage = int(kwargs.pop("max_leverage") or max(leverage_choices))

        leverage_choices = [(idx, '1:%i' % idx) for idx in leverage_choices if idx <= max_leverage]

        super(ChangeLeverageForm, self).__init__(*args, **kwargs)
        self.fields["leverage"].choices = leverage_choices

    def send_notification(self):
        notification_data = {"user_name": self.account.user.first_name, "account": self.account.mt4_id, "leverage": self.cleaned_data['leverage']}
        notification.send([self.account.user], self.notification_name, notification_data)

    def clean_leverage(self):
        leverage = int(self.cleaned_data["leverage"])
        return self.cleaned_data["leverage"]

    def save(self):
        issue = self.account.change_leverage(self.cleaned_data['leverage'])
        self.send_notification()
        return issue


class PasswordRecoveryForm(forms.Form):

    notification_name = "password_recovery"

    def send_notification(self, account, password):
        """Send account password recovery email to account user"""

        notification_data = {"user_name": account.user.first_name, "account": account.mt4_id, "password": password}
        notification.send([account.user], self.notification_name, notification_data,
                          no_django_message=True)

    def save(self, account):
        password = create_password()
        issue = account.change_password(password)
        self.send_notification(account, password)
        return issue


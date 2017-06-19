# -*- coding: utf-8 -*-
"""
Mt4 account registration form.
"""
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import transaction
from django.utils.encoding import force_unicode
from django.db.models import F, Func, Value
from django.core.urlresolvers import reverse

from gcrm.models import Contact
from notification.models import get_notification_language
from payments.systems.base import make_hidden
from platforms.forms import *
from platforms.models import TradingAccount
from platforms.mt4 import calculate_available_leverages

from platforms.types import *
from platforms.utils import create_password
from platforms.utils import get_ip
from private_messages.forms import notification
from project.utils import get_accept_fields
from registration.models import RegistrationProfile


class Mt4AccountForm(forms.Form):
    leverage = forms.ChoiceField(label=_("Leverage"))
    deposit = forms.IntegerField(label=_("Initial deposit"), min_value=0,
                                 help_text=_("Available to demo accounts only."))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        self.account_type = kwargs.pop("account_type", None)
        super(Mt4AccountForm, self).__init__(*args, **kwargs)
        if not self.account_type:
            return

        # Adding leverage choices and initial value (which defaults
        # to the first leverege choices item, if not set explicitly
        # in account type definition).
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

            if len(self.account_type.leverage_choices) == 1:
                self.fields["leverage"].widget = forms.HiddenInput()
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

        if self.account_type.available_options & HAS_BINARY_OPTIONS_TYPE_OPTIONS:
            self.fields["binary_options_type"] = forms.ChoiceField(
                label=_("Binary options style"),
                initial=EUROPEAN_OPTIONS,
                choices=BINARY_OPTIONS_TYPE_CHOICES,
                widget=forms.RadioSelect(),
                required=False,
                help_text=_("American-style options can be closed before expiration date, but have much lower "
                            "reward rate than European-style options"),
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
        if not self.account_type.leverage_choices and hasattr(self.account_type, 'leverage_default'):
            self.cleaned_data["leverage"] = self.account_type.leverage_default
        if self.account_type.available_options == \
                (HAS_EXECUTION_OPTIONS | HAS_CURRENCY_OPTIONS):
            self.cleaned_data["group"] = self.account_type. \
                group_choices[self.cleaned_data.get("execution_system")] \
                [self.cleaned_data.get("currency")]
        elif self.account_type.available_options == \
                (HAS_BINARY_OPTIONS_TYPE_OPTIONS | HAS_CURRENCY_OPTIONS):
            self.cleaned_data["group"] = self.account_type. \
                group_choices[self.cleaned_data.get("binary_options_type")] \
            [self.cleaned_data.get("currency")]
        elif self.account_type.available_options & HAS_EXECUTION_OPTIONS:
            self.cleaned_data["group"] = self.account_type. \
                group_choices[self.cleaned_data.get("execution_system")]
        elif self.account_type.available_options & HAS_CURRENCY_OPTIONS:
            self.cleaned_data["group"] = self.account_type. \
                group_choices[self.cleaned_data.get("currency")]
        elif self.account_type.available_options & HAS_BINARY_OPTIONS_TYPE_OPTIONS:
            self.cleaned_data["group"] = self.account_type. \
                group_choices[self.cleaned_data.get("binary_options_type")]
        elif self.account_type.group:
            self.cleaned_data["group"] = self.account_type.group
        else:
            self.cleaned_data["group"] = self.account_type.slug

        return self.cleaned_data

    @staticmethod
    def activation_url(user):
        """We need this to know, if the user is activated or not"""
        try:
            reg = RegistrationProfile.objects.get(user=user)
        except RegistrationProfile.DoesNotExist:
            return
        if reg.activation_key == 'ALREADY_ACTIVATED':
            return
        return reverse('registration_activate', args=[reg.activation_key])

    @transaction.atomic
    def save(self, profile=None, partner_api_id=None, additional_fields=None):
        profile = profile or self.request.user.profile
        user = profile.user
        password = create_password()
        Contact.objects.filter(user=user).exclude(tags__contains=['MetaTraider']).update(
            tags=Func(F('tags'), Value('MetaTraider'), function='array_append'))
        if self.account_type.is_demo:
            Contact.objects.filter(user=user).exclude(tags__contains=['demo']).update(
                tags=Func(F('tags'), Value('demo'), function='array_append'))
        else:
            Contact.objects.filter(user=user).exclude(tags__contains=['real']).update(
                tags=Func(F('tags'), Value('real'), function='array_append'))

        details = dict(
            # ip=get_ip(self.request),
            # ip='148.251.147.241',
            group=self.cleaned_data["group"],
            agent_account=profile.agent_code or 0,
            leverage=int(self.cleaned_data["leverage"]),
            password=password,
            # investor=create_password(),
            name="%s %s" % (user.first_name, user.last_name),
            email=user.email,
            # deposit=self.cleaned_data.get('deposit', ''),
            country=force_unicode(profile.country or ""),
            state=force_unicode(profile.state or ""),
            city=profile.city,
            address=profile.address,
            # id=user.pk,
            phone="",
            password_phone=create_password(size=6, only_digits=True),
            # send_reports=1,
            # read_only=0,
            # zipcode="perm_D1",  # Used by some custom GrandCapital mt4 system
            #master=settings.MT4_MASTER_PASSWORD
        )
        # if self.account_type.slug in read_only_slugs_oncreate():
            # pamm.types.LammMasterAccountType.slug  - realPAMM_1
            # pamm.types.LammInvestorAccountType.slug  - realPAMM_inv
            # mt4.types.RealOptionsAccountType.slug  - real_options_us
            # details['read_only'] = 1

        account_type_details = {
            'slug': self.cleaned_data.get("slug") or self.account_type.slug,
            'name': self.account_type.name,
            'is_demo': self.account_type.is_demo,
            'is_ib': self.account_type.is_ib_account,
            'engine': self.account_type.engine,
            'cookies': self.request.COOKIES,
            'host': self.request.get_host(),
            'ip': self.request.META['REMOTE_ADDR'],
        }

        with override('en'):
            account_type_details['name_en'] = unicode(self.account_type.name)

        from platforms.mt4.tasks import register_mt4account
        if self.save.async:
            task = register_mt4account.delay(details, user, account_type_details, self.__class__, partner_api_id,
                                             additional_fields)
            return task.task_id
        else:
            account_info = register_mt4account(details, user, account_type_details, self.__class__, partner_api_id,
                                               additional_fields)
            trading_acc = TradingAccount.objects.get(pk=account_info['account_pk'])
            login = trading_acc.mt4_id
            if self.cleaned_data.get('deposit'):
                trading_acc.change_balance(self.cleaned_data['deposit'], "Initial deposit")
            notification.send([user],
                              'demo_MT_account_created' if self.account_type.is_demo else 'real_MT_account_created',
                              {"password": password,
                               'type': self.account_type,
                               "login": login,
                               "account": login})

            return {"account": TradingAccount.objects.get(pk=account_info['account_pk']), "password": password}

    save.async = False  # Used in onestep.py to determine whether account is created sync/async

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
        # Email activation link
        notification_data['activation_url'] = cls.activation_url(account.user)

        recipients = [account.user]

        if getattr(cls, "notification_name", None):
            notification_name = cls.notification_name
        else:
            # HACK until WE HAZ ENGLISH
            notification_name = account_type.notification_name if get_notification_language(account.user) == "ru" \
                else "account_created"

        cls.get_notification().send(recipients, notification_name, notification_data,
                                    no_django_message=True)


class Mt4RealIBForm(Mt4AccountForm):
    notification_name = "realib_account_created"

    def __init__(self, *args, **kwargs):
        account_type = kwargs.pop("account_type", RealIBAccountType)
        super(Mt4RealIBForm, self).__init__(account_type=account_type, *args, **kwargs)
        self.fields['leverage'].widget = forms.HiddenInput()

    @transaction.atomic
    def save(self, profile=None, partner_api_id=None):
        return super(Mt4RealIBForm, self).save(profile, async=False, partner_api_id=partner_api_id)

    save.async = False

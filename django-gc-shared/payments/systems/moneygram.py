# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal
import re
from django.core.validators import MinValueValidator
from django.conf import settings
from django import forms
from django.utils.dateformat import format
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, ugettext
from currencies.currencies import USD
from payments.systems.base import (
    FormWithCity, FormWithCountry, FormWithName, FormWithTranslitedUppercaseName
)
from shared.widgets import DateWidget
from payments.systems import base


name = _("MoneyGram")
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "MGram"
logo = "moneygram.png"
currencies = ['USD']
display_amount = lazy(USD.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": lazy(lambda: ugettext("According to %s fees") % "MoneyGram", unicode),
        "time": _("a day"),
        "fee_large_deposit": lazy(lambda: ugettext("According to %s fees") % "MoneyGram", unicode),
    },
    "withdraw": {
        "time": _("up to 3 days"),
        "min_amount": display_amount(200),
        "fee": _("depends on the originating bank"),
    }
}

time_to_deposit = lambda: timedelta(1)

templates = {
    "deposit": "payments/forms/deposit/moneygram.html",
    "withdraw": "payments/forms/withdraw/wu_fastpost_moneygram.html",
}


class DepositForm(base.DepositForm, FormWithName, FormWithCountry, FormWithCity):
    commission_rate = Decimal(0)

    instructions = "payments/descriptions/moneygram/instructions.html"

    state = forms.CharField(label=_("State"), help_text=_("Only for transfers from the U.S."))
    address = forms.CharField(label=_("Address"), help_text=_("Please specify the address specified in transfer"))
    refnumber = forms.CharField(label=_("Referral number"),
                                help_text=_("8-digit verification number for the copy of the form. "
                                       "For example, 12345678"))
    answer = forms.CharField(label=_("Answer to the security question"),
                             help_text=_("Answer to the question specified while committing the transfer"))
    date_sent = forms.DateField(label=_("Date of transaction"), widget=DateWidget(),
                                help_text=_("Please specify the date the transfer was committed"))

    name_format = "%(first)s %(middle)s %(last)s"

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        # Populating required fields from the data we already have
        # (in UserProfile and User models).
        user = self.request.user
        profile = user.profile
        self.fields["state"].initial = getattr(profile, "state", None)
        self.fields["address"].initial = getattr(profile, "address", None)

        self.fields["name"].label = _("Sender")

        self.fields["country"].help_text = _("Please specify the country specified in transfer")
        self.fields["city"].help_text = _("Please specify the city specified in transfer")
        self.fields["name"].help_text = _("First name, last name. Please, fill in the data strictly in this order.")

        self.fields["amount"].validators = [MinValueValidator(10)]

        self.templates = ["payments/transfer_instructions.haml"] + self.templates

    def clean(self):
        if "refnumber" in self.cleaned_data:
            self.cleaned_data["purse"] = self.cleaned_data["refnumber"]
        return super(DepositForm, self).clean()

    def save(self, **kwargs):
        # HACK: because jsonfield's author is a total dickhead (p2).
        self.cleaned_data["date_sent"] = format(self.cleaned_data["date_sent"],
                                                settings.DATE_FORMAT)
        return super(DepositForm, self).save(**kwargs)


class DetailsForm(base.DetailsForm, FormWithTranslitedUppercaseName, FormWithCountry, FormWithCity):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        self.fields["country"].help_text = _("The country in which you receive transfer")
        self.fields["city"].help_text = _("The city in which you receive transfer")
        self.fields["purse"] = self.fields.pop("name")

    def clean_purse(self):
        if not re.match(r'^[A-Z -]*$', self.cleaned_data['purse']):
            raise forms.ValidationError(_('Only uppercase latin letters and space are allowed'))
        return self.cleaned_data['purse'].upper()


# -*- coding: utf-8 -*-
import re

from decimal import Decimal
from django import forms
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import RUR
from geobase.models import Country
from payments.systems import base
from payments.systems.base import (
    FormWithCity, FormWithCountry, FormWithName, PhonePursePaymentForm
)
from shared.widgets import DateWidget

name = u"Форсаж"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "Forsazh"
logo = "moneygram.png"
languages = ('ru',)
currencies = ['USD', 'EUR', 'RUB']
display_amount = lazy(RUR.display_amount, unicode)

transfer_details = {
    "withdraw": {
        "time": _("up to 3 days"),
        "min_amount": display_amount(5000),
        "fee": u"3%",
    }
}

templates = {
    "deposit": "payments/forms/deposit/moneygram.html",
    "withdraw": "payments/forms/withdraw/wu_fastpost_moneygram.html",
}


class DepositForm(base.DepositForm):
    pass


class DetailsForm(base.DetailsForm, FormWithName, FormWithCountry, FormWithCity, PhonePursePaymentForm):
    nationality = forms.ModelChoiceField(label=u"Гражданство", queryset=Country.objects.all())
    address = forms.CharField(label=u"Адрес", max_length=100, help_text=u"Адрес постоянной регистрации")
    document_type = forms.CharField(label=u"Тип документа", max_length=100, help_text=u"Тип документа, "
                                                                                      u"удостоверяющего личность")
    document_number = forms.CharField(label=u"Номер документа", max_length=100, help_text=u"Номер документа")
    document_issuer = forms.CharField(label=u"Кем выдан", max_length=100)
    document_issued_date = forms.DateField(label=u"Дата выдачи", widget=DateWidget())
    document_expiry = forms.DateField(label=u"Срок действия", widget=DateWidget(), required=False,
                                      help_text=u"Срок действия документа, удостоверяющего личность")
    birthday = forms.DateField(label=u"Дата рождения", widget=DateWidget())
    birthplace = forms.CharField(label=u"Место рождения", max_length=100)

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        self.fields["purse"].label = u"Номер телефона"
        self.fields["country"].help_text = _("The country in which you receive transfer")
        self.fields["city"].help_text = _("The city in which you receive transfer")

        profile = self.request.user.profile
        self.fields["purse"].initial = profile.phone_mobile
        self.fields["nationality"].initial = profile.country
        self.fields["birthday"].initial = profile.birthday

    def clean_purse(self):
        if not re.match(r'^[A-Z -]*$', self.cleaned_data['purse']):
            raise forms.ValidationError(_('Only uppercase latin letters and space are allowed'))
        return self.cleaned_data['purse'].upper()


class WithdrawForm(base.WithdrawForm):
    commission_rate = Decimal("0.03")

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s")
    )

    def __init__(self, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)

        # self.fields["country"].help_text = _("The country in which you receive transfer")
        # self.fields["city"].help_text = _("The city in which you receive transfer")
        self.fields["currency"].help_text = _("Choose currency")

    def _get_min_amount(self, account):
        return 5000, RUR
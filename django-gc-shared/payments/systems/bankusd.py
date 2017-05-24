# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import USD
from payments.systems import bankbase
from payments.systems.base import FormWithTranslitedName, CommissionCalculationResult

name = _("Bank transfer (USD)")
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "BANK USD"
logo = "bankusd.png"
currencies = ["USD"]

display_amount_usd = lazy(USD.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": _("depends on the originating bank"),
        "min_amount": display_amount_usd(500),
        "time": _("3 to 5 days"),
        "video_youtube_id": "fMnV1iT2Z30",
    },
    "withdraw": {
        "time": _("3 to 5 days"),
        "min_amount": display_amount_usd(100),
        "fee": display_amount_usd(40),
        "video_youtube_id": "_bLe5C3KNtY",
    }
}

time_to_deposit = lambda: timedelta(5)

templates = {
    "deposit": "payments/forms/deposit/bankusd.html",
    "withdraw": "payments/forms/withdraw/bankeur_usd.html"
}


class DepositForm(bankbase.DepositForm, FormWithTranslitedName):
    info = string_concat(
        _("Deposit of funds to the account - %(time)s"),
        "\n",
        _("USD transfer commission - %(fee)s"),
        "\n\n",
        _("Please fill out the form to request deposit of funds")
    )

    MIN_AMOUNT = (500, 'USD')

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        self.fields['name'].help_text = _('First, last and middle name (if any) in latin transcription. '
                                          'Example: Andrei Ivanovich Denisov')
        self.fields['country'].help_text = _('Country of residention of beneficiary')

        del (self.fields["passport_data"], self.fields["city"])

    @staticmethod
    def get_bank_base(self):
        return settings.BANKS['Verso']

    def clean(self):
        bankbase.clean_translify(self)

        return super(DepositForm, self).clean()


class DetailsForm(bankbase.DetailsForm, FormWithTranslitedName):

    #payment_details = forms.CharField(label=_("Details of payment"), required=False)

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        del self.fields['city']

        self.fields['name'].help_text = _('First, last and middle name (if any) in latin transcription. '
                                          'Example: Andrei Ivanovich Denisov')
        self.fields['name'].widget.attrs['readonly'] = True

        self.fields['country'].help_text = _('Country of residention of beneficiary')



    def clean(self):
        bankbase.clean_translify(self)

        return super(DetailsForm, self).clean()


class WithdrawForm(bankbase.WithdrawForm):
    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("USD transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds")
    )

    MIN_AMOUNT = (100, 'USD')


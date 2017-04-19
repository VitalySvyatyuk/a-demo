# -*- coding: utf-8 -*-
from datetime import timedelta

from django import forms
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat
from django.conf import settings

from currencies.currencies import RUR, EUR
from payments.systems import bankbase
from payments.systems.base import FormWithTranslitedName, CommissionCalculationResult


TRANSLATIONS = (
    _('Payment_Details'),
    _('Credit_Card_Number'),
)

name = _("Bank transfer (RUR)")
mt4_payment_slug = "BANK RUR"
slug = __name__.rsplit(".", 1)[-1]
logo = "bankrur.png"
currencies = ["RUR"]
languages = ('en', 'ru', 'id', 'zh-cn')

display_amount = lazy(RUR.display_amount, unicode)
display_amount_eur = lazy(EUR.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": _("depends on the originating bank"),
        "min_amount": display_amount(100),
        "time": _("3 to 5 days"),
        "video_youtube_id": "fMnV1iT2Z30",
    },
    "withdraw": {
        "time": _("3 to 5 days"),
        "min_amount": display_amount(100),
        "fee": display_amount_eur(40),
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
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of deposit - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request deposit of funds")
    )

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        self.fields['name'].help_text = _('First, last and middle name (if any) in latin transcription. '
                                          'Example: Andrei Ivanovich Denisov')

        self.fields['country'].help_text = _('Country of residention of beneficiary')

        del (self.fields["passport_data"], self.fields["city"])

    @staticmethod
    def get_bank_base(account):
        return settings.BANKS['Siauliu']

    def clean(self):
        bankbase.clean_translify(self)

        return super(DepositForm, self).clean()


class DetailsForm(bankbase.DetailsForm, FormWithTranslitedName):
    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        del self.fields['city']
        self.fields['name'].help_text = _('First, last and middle name (if any) in latin transcription. '
                                          'Example: Andrei Ivanovich Denisov')
        self.fields['country'].help_text = _('Country of residention of beneficiary')

    def clean(self):
        bankbase.clean_translify(self)

        return super(DetailsForm, self).clean()


class WithdrawForm(bankbase.WithdrawForm):
    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds"),
        "\n\n",
        _("<b>Please make sure </b> that your name in payment details matches the one in your account details"),
    )

    MIN_AMOUNT = (5000, 'RUR')

    @classmethod
    def _calculate_commission(cls, request):
        from decimal import Decimal
        from platforms.converter import convert_currency

        commission = 40

        commission = Decimal(convert_currency(commission, from_currency=EUR, to_currency=request.currency,
                                              for_date=request.creation_ts)[0])

        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

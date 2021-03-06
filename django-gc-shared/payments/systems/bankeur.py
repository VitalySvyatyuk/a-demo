# -*- coding: utf-8 -*-
from datetime import timedelta

from django.conf import settings
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import EUR
from payments.systems import bankbase
from payments.systems.base import FormWithTranslitedName, CommissionCalculationResult

name = _("Bank transfer (EUR)")
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "BANK EUR"
logo = "bankeur.png"
currencies = ["EUR"]

display_amount = lazy(EUR.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": _("depends on the originating bank"),
        "time": _("3 to 5 days"),
        "video_youtube_id" : "fMnV1iT2Z30",
    },
    "withdraw": {
        "time": _("3 to 5 days"),
        "min_amount": display_amount(200),
        "fee": display_amount(40),
        "video_youtube_id" : "_bLe5C3KNtY",
    },
}

time_to_deposit = lambda: timedelta(5)

templates = {
    "deposit": "payments/forms/deposit/bankeur.html",
    "withdraw": "payments/forms/withdraw/bankeur_usd.html"
}


class DepositForm(bankbase.DepositForm, FormWithTranslitedName):

    info = string_concat(
        _("Deposit of funds to the account - %(time)s"),
        "\n",
        _("Euro transfer commission - %(fee)s"),
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

    #payment_details = forms.CharField(label=_("Details of payment"), required=False)

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        del self.fields['city']

        self.fields['name'].help_text = _('First, last and middle name (if any) in latin transcription. '
                                          'Example: Andrei Ivanovich Denisov')
        self.fields['country'].help_text = _('Country of residention of beneficiary')

    def get_name(self):
        return super(DetailsForm, self).get_name()

    def clean(self):
        bankbase.clean_translify(self)

        return super(DetailsForm, self).clean()


class WithdrawForm(bankbase.WithdrawForm):

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Euro transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds")
    )

    MIN_AMOUNT = (100, 'EUR')

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



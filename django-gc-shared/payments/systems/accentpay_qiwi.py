# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import RUR
from platforms.converter import convert_currency
from payments.systems import accentpay, base

name = u"QIWI"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "monetaru.png"
languages = ('ru',)
currencies = ['RUR']

display_amount = lazy(RUR.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": u"3%",
        "time": _("15 minutes"),
    },
    "withdraw": {
        "fee": u"2%",
        "time": _("up to 3 days"),
    }
}

time_to_deposit = lambda: timedelta(minutes=15)


templates = {
    "deposit": "payments/forms/deposit/electronic.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}


class DepositForm(accentpay.DepositForm, base.PhonePursePaymentForm):
    commission_rate = Decimal("0.03")

    def __init__(self, *args, **kwargs):
        super(accentpay.DepositForm, self).__init__(*args, **kwargs)

    def get_additional_params(self):
        return {
            'followup': 1,
            'payment_group_id': 6,
            'phone': self.cleaned_data['purse'].replace('+', ''),
        }


class DetailsForm(base.DetailsForm, base.PhonePursePaymentForm, base.FormWithName):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = _("Receiver")
        self.fields["name"].help_text = _("Fill in your first, last and middle name (if any)")


class WithdrawForm(base.WithdrawForm):

    MAX_AMOUNT_PER_DAY = 500

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Maximal sum of withdrawal - %(max_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds")
    )

    commission_rate = Decimal("0.02")

    def clean(self):
        amount = convert_currency(self.cleaned_data["amount"], self.cleaned_data["currency"], "RUR")[0]

        if amount > 15000:
            self.add_error("amount", ValidationError(
                _("You cannot withdraw more than %(amount)s in one request") % {
                    "amount": display_amount(15000),
                }
            ))

        return super(WithdrawForm, self).clean()
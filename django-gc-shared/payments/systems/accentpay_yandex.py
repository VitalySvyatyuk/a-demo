# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import RUR
from payments.systems import accentpay, base

name = _("Yandex.Money")
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
    "deposit": "payments/forms/deposit/card.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}


class DepositForm(accentpay.DepositForm):
    commission_rate = Decimal("0.03")

    def get_additional_params(self):
        return {
            'followup': 1,
            'payment_group_id': 3,
        }


class DetailsForm(base.DetailsForm, base.FormWithName):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = _("Receiver")
        self.fields["name"].help_text = _("Fill in your first, last and middle name (if any)")


class WithdrawForm(base.WithdrawForm):

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds"),
        "\n\n",
        _("Attention! Funds withdrawal is only possible for the same currencies")
    )

    commission_rate = Decimal("0.02")
# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from currencies.currencies import RUR
from payments.systems import accentpay, base

name = u"VISA/MasterCard"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "monetaru.png"
currencies = ['RUR', 'EUR', 'USD']

display_amount = lazy(RUR.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": u"3%",
        "time": _("15 minutes"),
    },
    "withdraw": {
        "fee": u"3%",
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
            'payment_group_id': 1,
        }


class DetailsForm(base.DetailsForm):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        del self.fields["purse"]


class WithdrawForm(base.WithdrawForm):
    commission_rate = Decimal("0.03")
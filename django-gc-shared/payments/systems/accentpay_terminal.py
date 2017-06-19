# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal

from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from currencies.currencies import RUR
from payments.systems import accentpay

name = u"Терминал оплаты"
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
        "fee": u"",
        "time": "",
    }
}

time_to_deposit = lambda: timedelta(minutes=15)


templates = {
    "deposit": "payments/forms/deposit/card.html",
}


class DepositForm(accentpay.DepositForm):
    commission_rate = Decimal("0.03")

    def get_additional_params(self):
        return {
            'payment_group_id': 15,
        }
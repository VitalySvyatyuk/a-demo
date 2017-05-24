# -*- coding: utf-8 -*-
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

import payments.systems.accentpay
import payments.systems.bankbase
from payments.systems.bankusd import display_amount_usd
from payments.systems.base import CommissionCalculationResult
from payments.systems import base

name = u"Online banks"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "ecommpay.png"
languages = ('en', 'ru')
currencies = ['USD']

transfer_details = {
    "deposit": {
        "fee": u"3.5% min $0.53",
        "fee_large_deposit": u"3%",
        "min_amount": display_amount_usd(10),
        "time": _("Within day"),
    },
    "withdraw": {
        "fee": u"2.5%",
        "fee_large_deposit": u"3%",
        "min_amount": display_amount_usd(10),
        "time": _("Within day"),
    }
}

templates = {
    "deposit": "payments/forms/deposit/ecommpay.html",
    "withdraw": "payments/forms/withdraw/base.html"
}


class DepositForm(payments.systems.accentpay.DepositForm):
    action, auto = "https://terminal-sandbox.ecommpay.com/", True
    commission_rate = Decimal("0.035")
    MIN_AMOUNT = (10, 'USD')
    payment_group_id = "16"
    with_phone = False

class DetailsForm(base.DetailsForm):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        del self.fields["purse"]


class WithdrawForm(base.WithdrawForm):
    MIN_AMOUNT = (10, 'USD')


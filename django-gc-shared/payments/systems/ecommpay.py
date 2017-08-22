# -*- coding: utf-8 -*-
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

import payments.systems.accentpay
import payments.systems.bankbase
from payments.systems import base
from payments.systems.bankusd import display_amount_usd
from payments.systems.base import CommissionCalculationResult

name = u"Visa/Mastercard"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "ecommpay.png"
languages = ('en', 'ru')
currencies = ['USD']

transfer_details = {
    "deposit": {
        "fee": u"3.5% min $0.53",
        "min_amount": display_amount_usd(10),
        "time": _("Within day"),
    },
    "withdraw": {
        "fee": u"2.5%",
        "min_amount": display_amount_usd(10),
        "time": _("Within day"),
    }
}

templates = {
    "deposit": "payments/forms/deposit/ecommpay.html",
    "withdraw": "payments/forms/withdraw/visa-mastercard.html"
}


class DepositForm(payments.systems.accentpay.DepositForm):
    action, auto = "https://terminal.ecommpay.com/", True
    commission_rate = Decimal("0.035")
    MIN_AMOUNT = (10, 'USD')
    payment_group_id = "16"
    with_phone = False

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        min_comm = Decimal("0.53")
        commission = max(min_comm, commission)
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )


class DetailsForm(base.DetailsForm):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        del self.fields["purse"]


class WithdrawForm(base.WithdrawForm):
    MIN_AMOUNT = (10, 'USD')
    commission_rate = Decimal("0.025")

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

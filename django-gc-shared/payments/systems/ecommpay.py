# -*- coding: utf-8 -*-
from decimal import Decimal

from django.utils.translation import ugettext_lazy as _

import payments.systems.accentpay
import payments.systems.bankbase
from payments.systems.base import CommissionCalculationResult

name = u"Online banks"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "visa_mastercard.png"
languages = ('en', 'ru')
currencies = ['USD']

transfer_details = {
    "deposit": {
        "fee": u"3%",
        "fee_large_deposit": u"3%",
        "time": _("15 minutes"),
    },
    "withdraw": {
        "fee": u"3%",
        "fee_large_deposit": u"3%",
        "time": _("15 minutes"),
    }
}

templates = {
    "deposit": "payments/forms/deposit/ecommpay.html",
    "withdraw": "payments/forms/withdraw/bankeur_usd.html"
}


class DepositForm(payments.systems.accentpay.DepositForm):
    action, auto = "https://terminal-sandbox.ecommpay.com/", True
    commission_rate = Decimal("0.03")
    payment_group_id = "16"
    with_phone = False

    @classmethod
    def _calculate_commission(cls, request, full_commission):
        commission = request.amount * cls.commission_rate
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

# -*- coding: utf-8 -*-
import base64
import logging
from decimal import Decimal

import requests
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from currencies.currencies import decimal_round
from payments.systems import base
from payments.systems.bankusd import display_amount_usd
from payments.systems.base import CommissionCalculationResult

name = _("Naspay")
logo = "Naspay.jpg"
slug = __name__.rsplit(".", 1)[-1]
currencies = ["USD"]
mt4_payment_slug = "NASPAY"

transfer_details = {
    "deposit": {
        "fee": "2% min $1",
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    },
    "withdraw": {
        "fee": _("3.30% min $1 max $30"),
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    }
}

templates = {
    "deposit": "payments/forms/deposit/electronic.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}

log = logging.getLogger(__name__)


class DepositForm(base.DepositForm):

    bill_address = "https://demo.naspay.net/api/v1/transactions"
    get_token_url = "https://demo.naspay.net/auth/token"
    commission_rate = Decimal("0.035")
    MIN_AMOUNT = (10, 'USD')

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)
        del self.fields["purse"]

    @classmethod
    def is_automatic(cls, instance):
        return True

    def get_naspay_token(self):
        """
        :return: tuple. ('accessToken', 'Auth method'). Example: ("0.AQAAAU3in", "Bearer")
        or None if can't get token.
        """

        headers = {'Content-Type': 'application/json',
                   'Cache-Control': 'no-cache',
                   'Authorization': 'Basic ' + base64.b64encode(
                       settings.TERMINAL_KEY + ':' + settings.TERMINAL_SECRET)}


        result = requests.post(self.get_token_url, headers = headers)

        if result.status_code == 200:
            result = result.json()
        else:
            return None

        if result.get("accessToken"):
            return result.get("accessToken"), result.get("tokenType")
        else:
            return None

    def make_request(self):
        import json

        currency = {
            "USD": "USD"
        }.get(self.instance.currency, self.instance.currency)
        amount = int(decimal_round(self.instance.amount) * 100)
        token_tuple = self.get_naspay_token()

        if not token_tuple:
            return "Can't get the token."

        data = {
            "merchantTransactionId": unicode(self.instance.pk),
            "amount": amount,
            "currency": currency,
            "description": "Some thing"
        }

        headers = {'Content-Type': 'application/json', 'Authorization': token_tuple[1] + " " + token_tuple[0]}

        request = requests.post(self.bill_address, data=json.dumps(data), headers=headers)

        request = request.json()

        if request.get("transaction") and request.get("transaction").get("status") == "accepted":
            self.instance.refresh_state()
            self.instance.is_payed = True
            self.instance.params["transaction"] = request.get("transaction").get("id")
            self.instance.save()
            return None
        else:
            error_message = request.get("error").get("message") if request.get("error") else \
                "Automatic payment failed."
            self.instance.is_committed = False
            self.instance.is_payed = False
            self.instance.public_comment = error_message
            self.instance.save()
            return error_message

    @classmethod
    def generate_mt4_comment(cls, payment_request):
        return "{NASPAY}[%s]" % payment_request.pk

    def clean(self):
        from platforms.converter import convert_currency
        amount = self.cleaned_data["amount"]
        currency = self.cleaned_data["currency"]
        return super(DepositForm, self).clean()

    def confirmed_response_data(self, request):
        error = self.make_request()
        if error:
            return {'detail': "Error: %s" % error}, 400
        else:
            return {"success": True}, None

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        min_comm = Decimal("1")
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
        # self.fields["purse"].label = _("Net account")
        # self.fields["purse"].help_text = _("Your Neteller's 12-digit Account ID or email address that is "
        #                                    "associated with their NETELLER account")


class WithdrawForm(base.WithdrawForm):
    MIN_AMOUNT = (10, 'USD')
    commission_rate = Decimal("0.025")

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        min_comm = Decimal("1")
        max_comm = Decimal("30")
        commission = min(max_comm, max(min_comm, commission))
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

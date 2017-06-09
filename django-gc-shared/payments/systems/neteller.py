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

name = _("Neteller")
logo = "neteller.png"
slug = __name__.rsplit(".", 1)[-1]
currencies = ["USD"]
mt4_payment_slug = "NETELLER"

transfer_details = {
    "deposit": {
        "fee": "3.5% min $1",
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    },
    "withdraw": {
        "fee": _("2.5% min $1 max $30"),
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    }
}

templates = {
    "deposit": "payments/forms/deposit/neteller.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}

log = logging.getLogger(__name__)


class DepositForm(base.DepositForm):

    purse = forms.CharField(max_length=100, label=_("Net account"),
                            help_text=_("Your Neteller's 12-digit Account ID or email address that is "
                                        "associated with their NETELLER account"))
    secure_id = forms.IntegerField(label=_("Secure ID"), help_text=_("Your Neteller's 6-digit Secure ID"))

    bill_address = "https://api.neteller.com/v1/transferIn"
    get_token_url = "https://api.neteller.com/v1/oauth2/token?grant_type=client_credentials"
    commission_rate = Decimal("0.035")
    MIN_AMOUNT = (10, 'USD')

    @classmethod
    def is_automatic(cls, instance):
        return True

    def get_neteller_token(self):
        """
        :return: tuple. ('accessToken', 'Auth method'). Example: ("0.AQAAAU3in", "Bearer")
        or None if can't get token.
        """

        headers = {'Content-Type': 'application/json',
                   'Cache-Control': 'no-cache',
                   'Authorization': 'Basic ' + base64.b64encode(
                       settings.NETELLER_MERCHANT_ID + ':' + settings.NETELLER_SECRET_KEY)}


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
            "RUR": "RUB"
        }.get(self.instance.currency, self.instance.currency)
        amount = int(decimal_round(self.instance.amount) * 100)
        token_tuple = self.get_neteller_token()

        if not token_tuple:
            return "Can't get the token."

        data = {
            "paymentMethod": {
                "type": "neteller",
                "value": self.instance.purse
            },
            "transaction": {
                "merchantRefId": unicode(self.instance.pk),
                "amount": amount,
                "currency": currency
            },
            "verificationCode": unicode(self.instance.params["secure_id"]),
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
        return "{NETELLER}[%s]" % payment_request.id

    def clean(self):
        from platforms.converter import convert_currency
        amount = self.cleaned_data["amount"]
        currency = self.cleaned_data["currency"]
        if convert_currency(amount, currency, "USD")[0] < 30:
            self._errors["amount"] = [_("You can't deposit less than $30")]
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
        self.fields["purse"].label = _("Net account")
        self.fields["purse"].help_text = _("Your Neteller's 12-digit Account ID or email address that is "
                                           "associated with their NETELLER account")


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

# -*- coding: utf-8 -*-

#  NASPAY
#    IS
# DISABLED
#   NOW

# Не сделано:
# 1. подгружать данные пользователя и заполнять соответствующие поля
# 2. добавить id транзакции, чтобы было видно
# 3. изучить вопрос, можно ли передавать данные о карте для бэкофиса
# 4. проверить рус/англ.

import json
from decimal import Decimal
import base64
import logging

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
import requests
from currencies.currencies import decimal_round
import payments.systems.accentpay
import payments.systems.bankbase
from payments.systems import base
from payments.systems.bankusd import display_amount_usd
from payments.systems.base import CommissionCalculationResult
from django.http import HttpResponse, HttpResponseBadRequest

name = u"Naspay"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "NASPAY"
logo = "naspay.png"
languages = ('en', 'ru')
currencies = ['USD']

transfer_details = {
    "deposit": {
        "fee": "3% min $1",
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    },
    "withdraw": {
        "fee": _("3.30USD + 0.25% min $1 max $30"),
        "time": _("Within day"),
        "min_amount": display_amount_usd(10),
    }
}

templates = {
    "deposit": "payments/forms/deposit/naspay.html",
    "withdraw": "payments/forms/withdraw/naspay.html",
}

log = logging.getLogger(__name__)


class DepositForm(payments.systems.accentpay.DepositForm):
    action, auto = "https://naspay.com/payment/", True
    bill_address = "https://naspay.com/api/v1/transactions"
    get_token_url = "https://naspay.com/auth/token?grant_type=client_credentials"
    commission_rate = Decimal("0.030")
    MIN_AMOUNT = (10, 'USD')
    with_phone = False

    def get_naspay_token(self):
        """
        :return: tuple. ('accessToken', 'Auth method'). Example: ("0.AQAAAU3in", "Bearer")
        or None if can't get token.
        """

        headers = {'Content-Type': 'application/json',
                   'Cache-Control': 'no-cache',
                   'Authorization': 'Basic ' + base64.b64encode(
                       settings.TERMINAL_KEY + ':' + settings.TERMINAL_SECRET)}

        result = requests.get(self.get_token_url, headers=headers, )

        if result.status_code == 200:
            result = result.json()
        else:
            return None

        if result.get('access_token'):
            return result.get('access_token'), result.get('token_type')
        else:
            return None

    def make_request(self):
        import json

        currency = "USD"
        amount = int(decimal_round(self.instance.amount))
        token_tuple = self.get_naspay_token()

        if not token_tuple:
            return "Can't get the token."

        data = {
            "intent": "SALE",
            "amount": amount,
            "currency": currency,
            "merchantTransactionId": unicode(self.instance.pk),
            "description": "Payment for ARUM Capital",
        }

        headers = {'Content-Type': 'application/json', 'Authorization': token_tuple[1] + " " + token_tuple[0]}

        response = requests.post(self.bill_address, data=json.dumps(data), headers=headers)

        response = response.json()

        return response

    @property
    def mutate(self):
        assert hasattr(self, "instance")

        response = self.make_request()

        self.is_bound = False

        checkout_link = [l for l in response['links'] if l['rel'] == "checkout"][0]['href']

        self.action = checkout_link
        self.method = 'GET'
        self.fields = {}

        return self

    @classmethod
    def verify(cls, request):
        return True

    @classmethod
    def execute(cls, request, instance):

        data = json.loads(request.body)['transaction']

        if not data["merchantTransactionId"] == unicode(instance.pk):
            # log.debug("Naspay - data[merchantTransactionId] != unicode(instance.pk)")
            return HttpResponseBadRequest("FAIL")

        if data["state"] != "COMPLETED":
            instance.is_payed = False
            instance.is_committed = False
            instance.save()
            # log.debug("Naspay - data[state] != COMPLETED")
            return HttpResponse("CANCELED")

        instance.params["transaction"] = data["merchantTransactionId"]
        instance.is_payed = True
        instance.save()
        # log.debug("Naspay SUCCESS")
        return HttpResponse("SUCCESS")

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


class WithdrawForm(base.WithdrawForm):
    MIN_AMOUNT = (10, 'USD')
    commission_rate = Decimal("0.0025")
    fixed_commision = 3.30

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate + cls.fixed_commision
        min_comm = Decimal("1")
        max_comm = Decimal("30")
        commission = min(max_comm, max(min_comm, commission))
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )
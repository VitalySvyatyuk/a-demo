# -*- coding: utf-8 -*-
import base64
import hashlib
import hmac
import logging
from datetime import datetime, timedelta
from decimal import Decimal

import ipaddr
import requests
from django.conf import settings
from django.core.urlresolvers import reverse
from django.forms import ValidationError
from django.http import HttpResponse
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import RUR

from platforms.converter import convert_currency
from payments.systems import base
from payments.utils import build_absolute_uri

name = _("Qiwi")
slug = __name__.rsplit(".", 1)[-1]
currencies = ["USD"]
logo = "qiwi.png"
languages = ('ru', 'en')
mt4_payment_slug = "QIWI"
countries = 'russian'
with_purse_only = True

display_amount = lazy(RUR.display_amount, unicode)

# https://w.qiwi.ru/transfer.action
transfer_details = {
    "deposit": {
        "fee": "6%",
        "time": _("15 minutes"),
        "max_sum_in_day": 100000,
        "max_sum_in_month": 100000,
        "max_transactions_in_day": 40,
        "max_sum_one_time": 15000,
    },
    "withdraw": {
        "time": _("up to 3 days"),
        "max_amount": display_amount(15000),
        "fee": u"1%",
    }
}

time_to_deposit = lambda: timedelta(minutes=15)

templates = {
    "deposit": "payments/forms/deposit/electronic.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}


log = logging.getLogger(__name__)


class QIWI_ERRORS(object):
    OK = 0
    INVALID_SERVICE_CODE = 155  # Invalid service code (service-id should be 99)
    REPEATED_TRANSACTION = 215  # Payment with this transaction-number is already registered in QIWI Wallet
                                # but some other details of the request differ from the registered
    NOT_ENOUGH_FUNDS = 220  # Not enough funds available on the Agent's account
    AMOUNT_BELOW_LIMIT = 241  # Payment amount is less than the limit
    AMOUNT_ABOVE_LIMIT = 242  # Payment amount is greater than the limit
    INVALID_PHONE_NUMBER = 298  # Invalid phone number as user account ID
    UNKNOWN_ERROR = 300  # Unknown error. Contact QIWI Wallet technical support: xml-support@qiwi.ru
    TOO_SIMPLE_PASSWORD = 302  # The new password is too simple
    CREDITING_IS_BLOCKED = 319  # Crediting this user account is blocked
    WRONG_PHONE_NUMBER = 1019  # Wrong phone number


class DepositForm(base.DepositForm, base.PhonePursePaymentForm):
    callback_id_field = "bill_id"

    bill_address = "https://w.qiwi.com/api/v2/prv/%(shop)s/bills/%(transaction)s"
    redirect_address = "https://bill.qiwi.com/order/external/main.action?"
    commission_rate = Decimal("0.06")

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)
        self.fields["amount"].help_text = mark_safe(_(
            "<strong>Attention!</strong>"
            " If you do not have \"verified\" status with QIWI, please specify amount less than 15000 RUB."))

    @classmethod
    def is_automatic(cls, instance):
        return True

    @classmethod
    def verify(cls, request):

        request_ip = ipaddr.IPAddress(request.META["REMOTE_ADDR"])

        if not (request_ip in ipaddr.IPNetwork("91.232.230.0/23")
                or request_ip in ipaddr.IPNetwork("79.142.16.0/20")):
            return False

        dig = hmac.new(
            settings.QIWI_SECRET,
            msg=u"|".join(
                [request.POST["amount"], request.POST["bill_id"], request.POST["ccy"], request.POST["command"],
                 request.POST["comment"], request.POST["error"], request.POST["prv_name"], request.POST["status"],
                 request.POST["user"]]
            ).encode("utf-8"),
            digestmod=hashlib.sha1
        ).digest()

        return request.META.get("HTTP_X_API_SIGNATURE") == base64.b64encode(dig)

    @classmethod
    def execute(cls, request, instance):
        if instance.is_committed:
            log.debug("QIWI payment is already committed")
            return HttpResponse('<?xml version="1.0"?><result><result_code>0</result_code></result>',
                                content_type="text/xml")

        if Decimal(request.POST["amount"]) != instance.amount:
            log.debug("QIWI payment bad amount: %s != %s" % (request.POST["amount"], instance.amount))
            return HttpResponse()

        currency = request.POST["ccy"] if request.POST["ccy"] != "RUB" else "RUR"

        if currency != instance.currency:
            log.debug("QIWI payment bad currency: %s != %s" % (request.POST["ccy"], instance.currency))
            return HttpResponse()

        if request.POST["status"] == "paid":
            instance.is_payed = True
            instance.save()
            log.debug("QIWI payment ok")
            return HttpResponse('<?xml version="1.0"?><result><result_code>0</result_code></result>',
                                content_type="text/xml")
        else:
            instance.is_payed = False
            log.debug("QIWI payment bad status: %s" % request.POST["status"])
            instance.save()

        return HttpResponse()

    def clean(self):
        if 'currency' in self.cleaned_data and 'amount' in self.cleaned_data:
            amount = convert_currency(self.cleaned_data['amount'], self.cleaned_data['currency'], 'RUB',
                                      for_date=datetime.now().date())[0]
            # if amount > 15000:
            #     self.add_error('amount', _("QIWI doesn't support one-time payments of more "
            #                                "than 15000 roubles. If you need to deposit more "
            #                                "money via QIWI, just commit several payments."))
            if amount < 5:
                self.add_error('amount', _("Amount should be above 5 roubles"))

        return super(DepositForm, self).clean()

    def redirect(self):

        params = {
            "shop": settings.QIWI_PROVIDER_ID,
            "transaction": self.instance.id,
        }

        currency_map = {
            "RUR": "RUB"
        }

        # for qiwi, we should make 'put' request to make bill even before user redirected to it
        r = requests.put(
            self.bill_address % params,
            headers={
                "Accept": "application/json",
                "Authorization": "Basic %s" % base64.b64encode("%s:%s" % (settings.QIWI_LOGIN, settings.QIWI_PASSWORD))
            },
            data={
                "user": "tel:" + self.instance.purse,
                "amount": str(self.instance.amount.quantize(Decimal("0.01"))),
                "ccy": currency_map.get(self.instance.currency, self.instance.currency),
                "comment": str(self.instance.account.mt4_id),
                "lifetime": datetime.strftime(datetime.now() + settings.QIWI_REQUEST_LIFETIME, "%Y-%m-%dT%H:%M:%S"),
                "pay_source": "qw",
                "prv_name": "ArumPro Capital Ltd.",
            }
        )

        if r.ok and r.json()["response"]["result_code"] == QIWI_ERRORS.OK:
            from urllib import urlencode

            params.update(
                successUrl=build_absolute_uri(self.request, reverse("payments_operation_status",
                                                                   args=["deposit", self.instance.pk, "success"])),
                failUrl=build_absolute_uri(self.request, reverse("payments_operation_status",
                                                                args=["deposit", self.instance.pk, "fail"])),
            )
            return self.redirect_address + urlencode(params)

    def confirmed_response_data(self, request):
        redirect_to = self.redirect()
        if redirect_to is None:
            return {
                'detail': _('qiwi_bad_request')
            }, 400
        else:
            return {
                'redirect': redirect_to
            }, None


class DetailsForm(base.DetailsForm, base.PhonePursePaymentForm, base.FormWithName):

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)
        self.fields["name"].label = _("Receiver")
        self.fields["name"].help_text = _("Fill in your first, last and middle name (if any)")


class WithdrawForm(base.WithdrawForm):
    commission_rate = Decimal("0.01")

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("Rouble transfer commission - %(fee)s"),
        "\n",
        _("Maximal sum of withdrawal - %(max_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds")
    )

    # def clean(self):
    #     amount = convert_currency(self.cleaned_data["amount"], self.cleaned_data["currency"], "RUR")[0]
    #
    #     if amount > 15000:
    #         self.add_error("amount", ValidationError(
    #             _("You cannot withdraw more than %(amount)s in one request") % {
    #                 "amount": display_amount(15000),
    #             }
    #         ))
    #
    #     return super(WithdrawForm, self).clean()

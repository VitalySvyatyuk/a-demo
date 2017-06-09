# -*- coding: utf-8 -*-
import hashlib
from collections import OrderedDict
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseBadRequest
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _

from currencies.currencies import USD
from payments.systems import base
from payments.utils import build_absolute_uri

name = u"AccentPay"
slug = __name__.rsplit(".", 1)[-1]
mt4_payment_slug = "ACCPAY"
logo = "monetaru.png"
languages = ('ru',)
currencies = ["USD"]

display_amount = lazy(USD.display_amount, unicode)

transfer_details = {
    "deposit": {
        "fee": u"5%",
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


class DepositForm(base.DepositForm):
    action, auto = "https://terminal.accentpay.ru/", True

    commission_rate = Decimal("0.05")

    def get_additional_params(self):
        return {}

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)
        del self.fields["purse"]

    @classmethod
    def is_automatic(cls, instance):
        return True

    @classmethod
    def get_signature(cls, data):
        ordered = OrderedDict(sorted(data.items(), key=lambda t: t[0]))

        return hashlib.sha1(';'.join(("%s:%s" % (k, v) for k, v in ordered.items() if v)) +
                            ';' + settings.ACCENTPAY_SECRET).hexdigest()

    def mutate(self):
        assert hasattr(self, "instance")

        fail_url = build_absolute_uri(self.request, reverse("payments_operation_status", args=["deposit", self.instance.pk, "fail"]))
        success_url = build_absolute_uri(self.request, reverse("payments_operation_status", args=["deposit", self.instance.pk, "success"]))

        data = {
            "site_id": settings.ACCENTPAY_ACCOUNT,
            "external_id": unicode(self.instance.pk),
            "currency": "RUB" if self.cleaned_data['currency'] == "RUR" else self.cleaned_data['currency'],
            "amount": unicode(int(self.instance.amount*100)),
            "description": "Payment to account %s" % self.instance.account,
            "language": settings.LANGUAGE_CODE.lower(),
            "success_url": success_url,
            "decline_url": fail_url,
            "callback_method": "2",  # GET
            "followup": "1",
            "payment_group_id": "1"
        }

        data.update(self.get_additional_params())

        data["signature"] = self.get_signature(data)

        for field, value in data.iteritems():
            self.fields[field] = base.make_hidden(value)

        super(DepositForm, self).mutate()
        self.is_bound = False
        self.fields.pop('account')
        return self

    @classmethod
    def verify(cls, request):
        """Checks if a given object is allowed for execution."""

        if not request.POST:
            return False

        data = request.POST
        data_copied = data.dict()
        data_copied.pop('signature')
        return data["signature"] == cls.get_signature(data_copied)

    @classmethod
    def execute(cls, request, instance):

        data = request.POST

        currency = "RUR" if data["currency"] == "RUB" else data["currency"]

        if not (
            data["external_id"] == unicode(instance.pk)
            and currency == instance.currency
            and data["amount"] == unicode(int(instance.amount*100))
            and data["site_id"] == settings.ACCENTPAY_ACCOUNT
            and data["type_id"] in ("1", "3", "6")
        ):
            return HttpResponseBadRequest("FAIL")

        if data["status_id"] != "4":
            instance.is_payed = False
            instance.is_committed = False
            instance.save()
            return HttpResponse("CANCELED")

        instance.params["transaction"] = request.POST["transaction_id"]
        instance.is_payed = True
        instance.save()

        return HttpResponse("SUCCESS")

    @classmethod
    def generate_mt4_comment(cls, payment_request):
        return "{ACCPAY}[%s]" % payment_request.params["transaction"]

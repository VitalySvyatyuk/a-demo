# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal
from hashlib import md5
from logging import getLogger
from socket import gethostbyname

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, get_language, string_concat

from currencies.currencies import USD
from payments.systems import base
from payments.systems.bankusd import display_amount_usd
from payments.systems.base import CommissionCalculationResult
from payments.utils import build_absolute_uri
from platforms.types import RealMicroAccountType
from shared.validators import email_re

log = getLogger(__name__)

name = _("Skrill")
slug = __name__.rsplit(".", 1)[-1]
logo = "moneybookers.png"
mt4_payment_slug = "Skrill"
purse_regex = email_re
purse_example = "mb.customer@grandcapital.net"
currencies = ["USD"]

display_amount = lazy(USD.display_amount, unicode)

# https://www.moneybookers.com/app/help.pl?s=fees&fee_currency=USD
transfer_details = {
    "deposit": {
        "fee": u"3.5% min $1",
        "min_amount": display_amount_usd(10),
        "time": _("Within day"),
        "max_sum_one_time": 1000,
        "currency": USD,
        "video_youtube_id" : "627vnG_jVFw",
    },
    "withdraw": {
        "time": _("Within day"),
        "min_amount": display_amount(10),
        "fee": u"1.5% max $35",
        "currency": USD,
    }
}

time_to_deposit = lambda: timedelta(minutes=15)

templates = {
    "deposit": "payments/forms/deposit/card.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}


class DepositForm(base.DepositForm):
    action, auto = "https://www.moneybookers.com/app/payment.pl", True
    MIN_AMOUNT = (10, 'USD')
    commission_rate = Decimal("0.035")

    additional_parameters = {}

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)
        log.debug("Deposit Form init")

        self.fields["amount"].help_text = _("Amount of money to deposit in ")
        del self.fields["purse"]

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

    def mutate(self):
        log.debug("Mutating form")
        assert hasattr(self, "instance")

        # Getting current active language, and falling back to
        # english version if native isn't available.
        language = get_language().upper()
        if language == "ZH-CN":
            language = "CN"
        if language not in \
           "EN DE ES FR IT PL GR RO RU TR CN CZ NL DA SV FI".split():
            language = "EN"
        log.info("Language: {}".format(language))

        data = {"pay_to_email": settings.MONEYBOOKERS_TO[self.cleaned_data['currency']],
                "account": self.cleaned_data["account"].mt4_id,
                "status_url": build_absolute_uri(self.request,
                    reverse("payments_operation_result",
                            args=[self.instance.pk])),
                "return_url": build_absolute_uri(self.request,
                    reverse("payments_operation_status",
                            args=["deposit", self.instance.pk, "success"])),
                "cancel_url": build_absolute_uri(self.request,
                    reverse("payments_operation_status",
                            args=["deposit", self.instance.pk, "fail"])),
                "language": language,
                "detail1_description": "Account:",
                "logo_url": "https://arumcapital.eu/static/img/marketing-site/etc/logo-arum--word.png",
                "detail1_text": self.cleaned_data["account"]}

        data.update(self.additional_parameters)
        log.debug("Data is {}".format(data))

        for field, value in data.iteritems():
            self.fields[field] = base.make_hidden(value)

        return super(DepositForm, self).mutate()

    @staticmethod
    def verify(request):
        """
        Returns True if a given request object is a valid Skrill
        request and False othewise.
        """
        log.info("Verifying Skrill callback form")
        secret = md5(settings.MONEYBOOKERS_SECRET).hexdigest().upper()
        data = dict(request.POST.iteritems(), secret=secret)
        log.debug("Data: {}".format(data))
        calc_md5 = md5(u"".join(data.get(k) for k in (
            "merchant_id", "transaction_id", "secret", "mb_amount",
            "mb_currency", "status"
            ))).hexdigest()
        recv_md5 = data["md5sig"].lower()
        log.debug("Calc: {} Recv: {}".format(calc_md5, recv_md5))

        return calc_md5 == recv_md5

    @staticmethod
    def execute(request, instance):
        """
        Proxies incoming Moneybookers request to the MetaTrader server,
        updating DepositRequest instance with operation result.
        """
        log.info("Deposit form execution")
        data = request.POST
        # Status codes:
        # | code | reason    |
        # |------+-----------|
        # |   -2 | failed    |
        # |   -1 | cancelled |
        # |    0 | pending   |
        # |    2 | processed |
        if int(data["status"]) < 0:
            log.warn("Payment failed/cancelled")
            return HttpResponse()

        data = {"ip": gethostbyname(request.META["SERVER_NAME"]),
                "account": instance.account.mt4_id,
                "amount": data["mb_amount"],
                "payfrom": data["pay_from_email"],
                "payto": data["pay_to_email"],
                "transaction": data["transaction_id"],
                "merchant": data["merchant_id"],
                "currency": data["mb_currency"],
                "status": data["status"],
                "md5": data["md5sig"]}
        log.debug("Data: {}".format(data))

        if instance.amount == Decimal(data["amount"]) and data["currency"] == instance.currency:
            instance.is_payed = True
        else:
            instance.is_payed = False
            instance.is_committed = False
            instance.private_comment = "Received payment confirmation with WRONG amount and/or currency"

        instance.params['transaction_id'] = unicode(data["transaction"])

        if "cc_last_4digits" in request.POST:
            log.info("Has last 4 CC digits: {}".format(request.POST["cc_last_4digits"]))
            instance.params["cardnumber"] = request.POST["cc_last_4digits"]

        instance.save()

        return HttpResponse("OK")

    @classmethod
    def generate_mt4_comment(cls, payment_request):
        transaction_id = payment_request.params.get('transaction_id', payment_request.id)
        return "{Skrill}[%s]" % transaction_id


class DetailsForm(base.DetailsForm):
    pass


class WithdrawForm(base.WithdrawForm):

    info = string_concat(
        _("Withdrawal of funds from the account - %(time)s"),
        "\n",
        _("USD transfer commission - %(fee)s"),
        "\n",
        _("Minimal sum of withdrawal - %(min_amount)s"),
        "\n\n",
        _("Please fill out the form to request withdrawal of funds")
    )
    MIN_AMOUNT = (10, 'USD')
    commission_rate = Decimal("0.015")

    def __init__(self, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)

    def _get_min_amount(self, account):
        # only one withdraw currency allowed (web-development-2759)
        return 1 if account.group == RealMicroAccountType else 10, 'USD'

    @classmethod
    def _calculate_commission(cls, request, full_commission=False):
        commission = request.amount * cls.commission_rate
        max_comm = Decimal("35")
        commission = min(max_comm, commission)
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

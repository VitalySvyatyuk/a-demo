# -*- coding: utf-8 -*-
from datetime import timedelta
from decimal import Decimal
from socket import gethostbyname
from hashlib import md5
from platforms.converter import convert_currency

from shared.validators import email_re
from django.core.validators import MinValueValidator
from django.core.urlresolvers import reverse
from django.conf import settings
from django.http import HttpResponse
from django.utils.functional import lazy
from django.utils.translation import ugettext_lazy as _, get_language, string_concat

from currencies.currencies import USD
from platforms.types import RealMicroAccountType
from payments.systems import base
from payments.systems.base import CommissionCalculationResult
from payments.utils import build_absolute_uri


name = _("Skrill")
slug = __name__.rsplit(".", 1)[-1]
logo = "skrill.png"
mt4_payment_slug = "Skrill"
purse_regex = email_re
purse_example = "mb.customer@grandcapital.net"
currencies = ["USD"]

# Password for the account above is: k02LVey6Ibv1ZmrU
# Birth date: 11.05.1988

display_amount = lazy(USD.display_amount, unicode)

# https://www.moneybookers.com/app/help.pl?s=fees&fee_currency=USD
transfer_details = {
    "deposit": {
        "fee": "1.9% + $0.33",
        "time": _("15 minutes"),
        "max_sum_one_time": 1000,
        "currency": USD,
        "video_youtube_id" : "627vnG_jVFw",
    },
    "withdraw": {
        "time": _("up to 3 days"),
        "min_amount": display_amount(10),
        "fee": u"1%",
    }
}

time_to_deposit = lambda: timedelta(minutes=15)

templates = {
    "deposit": "payments/forms/deposit/card.html",
    "withdraw": "payments/forms/withdraw/electronic.html",
}


class DepositForm(base.DepositForm):
    action, auto = "https://www.moneybookers.com/app/payment.pl", True

    additional_parameters = {}

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        # Forcing a minimum of 10 currency units for withdrawal.
        self.fields["amount"].validators = [MinValueValidator(10)]
        self.fields["amount"].help_text = _("Amount of money to deposit in "
                                            "USD (at least 10 currency units)")
        del self.fields["purse"]

    @classmethod
    def _calculate_commission(cls, request, full_commission):
        from profiles.models import UserProfile
        if not full_commission:  # and (request.account.user.profile.payback_status == UserProfile.PAYBACK_STATUS.GOLD or
                                 #    request.amount >= convert_currency(300, "USD", request.currency)[0]):
            commission = 0
        else:
            commission = (request.amount * Decimal("0.019")) + Decimal(convert_currency(0.33, "USD", request.currency)[0])
        return CommissionCalculationResult(
            amount=request.amount,
            commission=commission,
            currency=request.currency
        )

    def mutate(self):
        assert hasattr(self, "instance")

        # Getting current active language, and falling back to
        # english version if native isn't available.
        language = get_language().upper()
        if language == "ZH-CN":
            language = "CN"
        if language not in \
           "EN DE ES FR IT PL GR RO RU TR CN CZ NL DA SV FI".split():
            language = "EN"

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

        for field, value in data.iteritems():
            self.fields[field] = base.make_hidden(value)

        return super(DepositForm, self).mutate()

    @staticmethod
    def verify(request):
        """
        Returns True if a given request object is a valid Moneybookers
        request and False othewise.

        See Anex III in Moneybookers Gateway Manual
        http://moneybookers.com/merchant/en/moneybookers_gateway_manual.pdf
        """
        secret = md5(settings.MONEYBOOKERS_SECRET).hexdigest().upper()
        data = dict(request.POST.iteritems(), secret=secret)

        return md5(u"".join(data.get(k) for k in (
            "merchant_id", "transaction_id", "secret", "mb_amount",
            "mb_currency", "status"
            ))).hexdigest() == data["md5sig"].lower()

    @staticmethod
    def execute(request, instance):
        """
        Proxies incoming Moneybookers request to the MetaTrader server,
        updating DepositRequest instance with operation result.
        """
        data = request.POST
        # Status codes:
        # | code | reason    |
        # |------+-----------|
        # |   -2 | failed    |
        # |   -1 | cancelled |
        # |    0 | pending   |
        # |    2 | processed |
        if int(data["status"]) < 0:
            return HttpResponse()  # Payment failed, but that's allright.

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

        if instance.amount == Decimal(data["amount"]) and data["currency"] == instance.currency:
            instance.is_payed = True
        else:
            instance.is_payed = False
            instance.is_committed = False
            instance.private_comment = "Received payment confirmation with WRONG amount and/or currency"

        instance.params['transaction_id'] = unicode(data["transaction"])

        if "cc_last_4digits" in request.POST:
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

    def __init__(self, *args, **kwargs):
        super(WithdrawForm, self).__init__(*args, **kwargs)

    def _get_min_amount(self, account):
        # only one withdraw currency allowed (web-development-2759)
        return 1 if account.group == RealMicroAccountType else 10, 'USD'

    @classmethod
    def _calculate_commission(cls, request):
        from profiles.models import UserProfile
        if request.account.user.profile.payback_status == UserProfile.PAYBACK_STATUS.GOLD:
            c = 0
        else:
            c = min(Decimal("0.68"), request.amount/100)
        return CommissionCalculationResult(
            amount=request.amount,
            commission=c,
            currency=request.currency
        )

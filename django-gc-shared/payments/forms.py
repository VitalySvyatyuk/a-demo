# -*- coding: utf-8 -*-
import re
from json import dumps

from django import forms
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import ugettext_lazy as _

from payments.models import (
    TypicalComment, WithdrawRequestsGroupApproval, WithdrawRequest, AdditionalTransaction
)
from platforms.exceptions import PlatformError
from platforms.models import TradingAccount, AbstractTrade


class WithdrawRequestsGroupApprovalForm(forms.ModelForm):
    class Meta:
        model = WithdrawRequestsGroupApproval
        fields = ['is_accepted', 'comment']


class WithrawRequestFastDeclineForm(forms.ModelForm):
    comment_choices = TypicalComment.objects.filter(for_withdraw=True, public=False)
    reason_choices = TypicalComment.objects.filter(for_withdraw=True, public=True)

    needs_manager_attention = forms.BooleanField(
        label=_("Needs manager's attention"),
        required=False,
        help_text=_("Manager will receive a task in the CRM"))

    class Meta:
        model = WithdrawRequest
        fields = ['public_comment', 'private_comment']


class AdditionalTransactionForm(forms.ModelForm):

    class Meta:
        fields = ("account", "amount", "currency", "symbol", "comment", "by")
        model = AdditionalTransaction

        widgets = {
            'by': forms.HiddenInput,
        }

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop("request")

        super(AdditionalTransactionForm, self).__init__(*args, **kwargs)

        self.fields["account"] = forms.CharField(label=_("Account"), help_text="...")

        self.fields["symbol"] = forms.CharField(label=_("Transaction type"), help_text="...")

        choices = cache.get("payments_mt4_comment_choices", [])
        if not choices:
            for x in (AbstractTrade.objects.filter(cmd=6).values("comment").order_by().annotate(Count("comment"))
                                      .order_by("-comment__count")[:100]):
                # убираем из комментария информацию о том, кто провел платеж изначально
                c = re.sub("^<\d*>", "", x["comment"])
                choices.append(c)
            cache.set("payments_mt4_comment_choices", choices, 60*60*24)  # timeout in seconds = 1 day

        self.fields["comment"].choices = dumps(choices)
        self.fields["currency"].initial = "USD"

    def clean_account(self):

        mt4_id = self.cleaned_data["account"]
        accs = TradingAccount.objects.filter(mt4_id=mt4_id)
        if not accs:
            raise ValidationError(_("No such account"))
        return accs[0]

    # автозаполнение поля "автор" :)
    def clean_by(self):
        return self.request.user

    def clean(self):

        amount = self.cleaned_data.get("amount")
        account = self.cleaned_data.get("account")
        currency = self.cleaned_data.get("currency")
        symbol = self.cleaned_data.get("symbol")
        comment = self.cleaned_data.get("comment")

        if not (amount and account and currency and symbol and comment):
            return self.cleaned_data

        if symbol == "Bonus":
            comment = comment.strip("()")
        else:
            if amount < 0 and abs(amount) > account.get_balance(currency=currency)[0]:
                raise ValidationError(_("Not enough funds on account"))

        return self.cleaned_data

    def save(self, *args, **kwargs):
        obj = super(AdditionalTransactionForm, self).save(*args, **kwargs)

        try:
            res = obj.account.change_balance(
                amount=obj.amount,
                comment=obj.comment,
                request_id="manual_%s" % obj.id,
                transaction_type=obj.symbol,
                amount_currency=obj.currency,
            )

            obj.trade_id = res["order_id"]
            return obj.save()
        except PlatformError as e:
            pass

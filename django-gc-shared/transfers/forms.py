# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, string_concat

from currencies.currencies import get_currency
from issuetracker.models import InternalTransferIssue
from platforms.exceptions import PlatformError
from platforms.converter import convert_currency
from platforms.models import TradingAccount
from platforms.types import RealIBAccountType
from notification import models as notification

import logging

log = logging.getLogger(__name__)


class InternalTransferForm(forms.ModelForm):
    MODE_CHOICES = (
        # ('auto', _("Transfer between your accounts")),
        ('manual', _("Transfer to another customer")),
    )

    template = "payments/forms/transfer.html"

    sender = forms.ModelChoiceField(label=_("Account"), help_text=_("Select one of your accounts."),
                                    queryset=TradingAccount.objects.none())
    recipient_auto = forms.ModelChoiceField(label=_("Recipient"), queryset=TradingAccount.objects.none(),
                                            required=False)
    recipient_manual = forms.IntegerField(label=_("Recipient"), required=False)
    mode = forms.ChoiceField(label=_("Type of transfer"),
                             widget=forms.HiddenInput, choices=MODE_CHOICES, initial="manual",
                             help_text=_("Transfers between your own account happen automatically, "
                                         "transfers to other customers are carried out manually")
                             )

    class Meta:
        model = InternalTransferIssue
        fields = ("sender", "recipient", "amount", "currency")

        widgets = {
            "recipient": forms.HiddenInput
        }

    def __init__(self, *args, **kwargs):
        log.info("Initiating internal transfer")
        self.account = kwargs.pop("account", None)
        self.request = kwargs.pop('request')
        self.internal = kwargs.pop('internal', False)  # Internal (staff) usage, everything is allowed

        log.debug("acc={} req={} internal={}".format(self.account, self.request, self.internal))
        super(InternalTransferForm, self).__init__(*args, **kwargs)

        if self.internal:
            self.fields["sender"] = forms.CharField(label=_("Account"), help_text=_("Select one of your accounts."),
                                                    max_length=100)
        else:
            qs = TradingAccount.objects.alive().non_demo().filter(user=self.request.user, is_deleted=False)

            self.fields['sender'].queryset = qs
            self.fields['recipient_auto'].queryset = qs

        if self.account:
            try:
                account = self.request.user.accounts.get(mt4_id=int(self.account))
            except (TradingAccount.DoesNotExist, TypeError):
                log.warn('Account id cannot not be finded for {}'.format(self.account))
                self.account = None
            else:
                self.account = account
                self.fields['sender'].initial = self.account

    def clean_amount(self):
        log.debug("Clean amount")
        if self.cleaned_data["amount"] <= 0:
            raise forms.ValidationError(_("Enter a valid transfer amount."))
        return self.cleaned_data["amount"]

    def clean_sender(self):
        log.debug("Clean sender")
        sender = self.cleaned_data["sender"]
        log.debug("sender={}".format(sender))

        if self.internal:
            sender = TradingAccount.objects.get(id=sender)

        if sender.is_disabled:
            raise ValidationError(_("You can't transfer funds from this account"))

        if sender.is_demo or sender.no_inout:
            raise forms.ValidationError(_("You can't transfer money from demo account"))

        if sender.group is None:
            raise forms.ValidationError(_('Cannot determine the group of sender account'))

        if sender.group in (RealIBAccountType,):
            raise forms.ValidationError(_('Internal transfers are not available for %s account group')
                                        % unicode(sender.group))

        return sender

    def clean(self):
        log.debug("Form clean")
        if self.errors:
            log.debug("There are errors!")
            return self.cleaned_data

        sender = self.cleaned_data["sender"]
        amount = self.cleaned_data["amount"]
        mode = self.cleaned_data["mode"]
        currency = get_currency(self.cleaned_data["currency"])
        log.debug("sender={} amount={} mode={} curr={}".format(sender, amount, mode, currency))

        # Delete in Arum?
        if sender.group == RealIBAccountType and not sender.verification.exists():
            self._errors["sender"] = [mark_safe(
                _('You should <a href="%(link)s" target="_blank">complete the verification process</a> '
                  'before withdrawing from account %(account)s') % {
                    'account': sender.mt4_id,
                    'link': reverse("referral_verify_partner") + "?next=" + self.request.path
                }
            )]
            return self.cleaned_data

        try:
            log.debug("Checking sender balance")
            from payments.systems.base import WithdrawForm
            withdraw_limit, bonuses = WithdrawForm.get_withdraw_limit_data(sender)
            withdraw_limit = withdraw_limit.to(currency)
        except:
            log.error("Can't get balance for sender {}".format(sender))
            self._errors["sender"] = [_("Error while getting allowed transfer amount for the "
                                        "chosen account. Contact the administrator.")]
            return self.cleaned_data
        from decimal import Decimal
        if amount > Decimal(withdraw_limit.amount).quantize(Decimal("0.01")):
            log.warn("User asked sum greater then available ({}>{})".format(amount, withdraw_limit))
            self._errors["amount"] = [
                _("The maximum amount of money you can transfer from the chosen "
                  "account is %(limit_value)s ") % {"limit_value": withdraw_limit}
            ]

        log.debug("Converting currency")
        converted_amount, currency = convert_currency(amount, currency, sender.currency, silent=False)

        if converted_amount < 0.01:
            log.warn("Sum is less then one cent after conversion!")
            self._errors["amount"] = [_("You cannot transfer less than 0.01 in chosen currency")]

        if mode == "manual":
            log.debug("Manual mode")
            recipient_field_name = "recipient_manual" if self.internal else "recipient_auto"

            if not self.cleaned_data[recipient_field_name]:
                self._errors[recipient_field_name] = [_("This field is required")]
                return self.cleaned_data
            # ♿ the problem is we sent other data type when we use self.internal through admin panel
            recipient_id = self.cleaned_data[recipient_field_name] if self.internal else self.cleaned_data[
                recipient_field_name].mt4_id
            recipients = TradingAccount.objects.filter(mt4_id=recipient_id)

            if recipients:
                recipient = recipients[0]
                log.debug("Recepient: {}".format(recipient))
            else:
                self._errors["recipient_manual"] = [
                    _("This account seems not to be registered in the private office. Register it first.")
                ]
                return self.cleaned_data
        else:
            log.debug("Auto mode")
            recipient_field_name = "recipient_auto"

            if not self.cleaned_data[recipient_field_name]:
                self._errors[recipient_field_name] = [_("This field is required")]
                return self.cleaned_data

            recipient = self.cleaned_data[recipient_field_name]
            log.debug("Recepient: {}".format(recipient))

        if recipient.is_demo or recipient.no_inout:
            self._errors[recipient_field_name] = [_("You can't transfer money to demo account")]

        if recipient.group is None:
            log.warn("Cant find group for recepient acc: {}".format(recipient))
            self._errors[recipient_field_name] = [_('Cannot determine the group of recipient account')]

        # Making sure that a user can't request a transfer, using a single
        # account as both recipient and sender.
        if sender.mt4_id == recipient.mt4_id:
            self._errors[recipient_field_name] = [_("Using the same account for both "
                                                    "recipient and sender is not allowed.")]

        self.recipient = recipient
        self.cleaned_data["recipient"] = recipient.mt4_id

        return self.cleaned_data

    def save(self, **kwargs):
        log.info("Saving internal transfer issue")
        amount = self.cleaned_data['amount']
        recipient = self.recipient
        sender = self.cleaned_data['sender']
        currency = get_currency(self.cleaned_data["currency"])
        manual = self.cleaned_data["mode"] == "manual"
        log.info("Transfering {amount} {curr} from {sender} to {recipient}".format(
            amount=amount, curr=currency, sender=sender, recipient=recipient))

        if manual and not self.internal:
            # If manual then only issue is created
            result = super(InternalTransferForm, self).save(**kwargs)
            log.debug("Notification: manual_transfer_submitted")
            notification.send([sender.user], "manual_transfer_submitted",
                              {
                                  'sender': sender, 'recipient': recipient,
                                  'amount': amount, 'issue': result,
                              })
            send_mail(
                "New issue for internal transfer created",
                'sender: {}, recipient: {}\namount: {}, issuetracker: {}'
                    .format(sender, recipient, amount,
                            'arumcapital.eu' + reverse("admin:issuetracker_internaltransferissue_change",
                                                       args=(result.id,))),
                settings.SERVER_EMAIL,
                settings.BACKOFFICE
            )
            return result

        withdraw_done = False
        deposit_done = False
        bonus_amount = -1

        try:
            sender.check();
            recipient.check()
            log.info("Withdrawing {}".format(sender))
            sender.change_balance(-float(amount), amount_currency=currency,
                                  comment="Wdraw IT '%s'" % recipient.mt4_id, request_id=0,
                                  transaction_type="InternalTransfer")
            withdraw_done = True

            log.info("Depositing {}".format(recipient))
            recipient.change_balance(float(amount), amount_currency=currency,
                                     comment="Deposit IT '%s'" % sender.mt4_id, request_id=0,
                                     transaction_type="InternalTransfer")
            deposit_done = True

            # нужно вернуть что-то отличное от None
            return "ok"

        except PlatformError as e:
            log.error("Error transfering funds: {}".format(e.message))
            if e.code == e.NOT_ENOUGH_MONEY:
                if self.internal:
                    self.errors["__all__"] = _("Sender equity level is insufficient for this operation.")

            msg = "During funds transfer %(from)s => %(to)s error happened. Exactly:\n\n"

            if withdraw_done:
                msg += "- successful withdrawal of %(from_amount)s from %(from)s\n"

                if deposit_done:
                    msg += "- successful deposition of %(to_amount)s to %(to)s\n"
                else:
                    msg += "- failed deposition of %(to_amount)s to %(to)s [" + unicode(e) + u"]\n"
            else:
                msg += "- failed withdrawal of %(from_amount)s from %(from)s [" + unicode(e) + u"]\n"

            kwargs = {
                "from": sender,
                "to": recipient,
                "from_amount": currency.display_amount(amount),
                "to_amount": currency.display_amount(amount),
                "bonus_amount": sender.currency.display_amount(bonus_amount) if bonus_amount is not None else "",
            }

            log.info("Sending emails about failed transfer")
            log.debug("To: {}".format(settings.MANAGERS))
            log.debug("Text: {}".format(msg % kwargs))
            send_mail(
                "Internal transfer %(from)s -> %(to)s FAIL" % kwargs,
                msg % kwargs,
                settings.SERVER_EMAIL,
                [x[1] for x in settings.MANAGERS]
            )
            if self.internal:
                self.errors["__all__"] = (msg % kwargs)

    def render_form(self):
        return render_to_string(
            self.template, RequestContext(self.request, {
                'form': self,
                "PAYMENTS_RECEIVER": settings.PAYMENTS_RECEIVER
            }))
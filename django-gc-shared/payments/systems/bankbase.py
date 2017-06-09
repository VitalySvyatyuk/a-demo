# -*- coding: utf-8 -*-
import re
from hashlib import md5

from django import forms
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _
from pytils.translit import translify

from geobase.models import Country
from payments.systems import base
from payments.systems.base import FormWithCountry, FormWithCity

# A hack for gettext to see the translations of field names
TRANSLATIONS = (
    _('Correspondent'),
    _('Passport_Data'),
    _('Bank_Account'),
    _('Tin'),
    _('Bic'),
)

templates = {
    "deposit": "payments/forms/deposit/bank.html",
    "withdraw": "payments/forms/withdraw/bankeur_usd.html",
}

# http://en.wikipedia.org/wiki/International_Bank_Account_Number#IBAN_formats_by_country
IBAN_COUNTRIES_CODES = ["AE", "AD", "AL", "AT", "AZ",
                        "BA", "BE", "BG", "BH", "BR",
                        "CH", "CR", "CY", "CZ",
                        "DE", "DK", "DO",
                        "EE", "ES",
                        "FO", "FI", "FR",
                        "GB", "GE", "GI", "GL", "GR", "GT",
                        "HR", "HU",
                        "IS", "IE", "IL", "IT",
                        "KZ", "KW",
                        "LV", "LB", "LI", "LT", "LU",
                        "MC", "MD", "ME", "MK", "MR", "MT", "MU",
                        "NL", "NO",
                        "PK", "PL", "PS", "PT",
                        "RE", "RO", "RS",
                        "SA", "SI", "SK", "SM", "SE",
                        "TN", "TR",
                        "VG"]


def validate_iban(value):
    """
    Validate IBAN number.
    Args:
        value: string with IBAN.

    Returns:
        True if it's valid, else False.

    See Also:
        http://en.wikipedia.org/wiki/International_Bank_Account_Number#Validating_the_IBAN
    """
    assert isinstance(value, str)
    # Delete spaces
    value = "".join(re.compile("[\d\w]+").findall(value.upper()))
    # Move first 4 letters to the end
    value = value[4:] + value[:4]
    # Replace letters: A=10, ..., Z=35
    replaces = [(chr(x+55), str(x)) for x in xrange(10, 36)]
    for old, new in replaces:
        value = value.replace(old, new)

    # Check if it is number
    assert re.compile("\d+").match(value)
    # Must be remainder of 1 after division
    return int(value) % 97 == 1


class DepositForm(base.DepositForm, FormWithCountry, FormWithCity):

    info = _("bankbase.deposit.info")

    address = forms.CharField(label=_("Address"))
    passport_data = forms.CharField(label=_("Passport data"), widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(DepositForm, self).__init__(*args, **kwargs)

        # Populating required fields from the data we already have
        # (in UserProfile and User models).
        user = self.request.user
        profile = user.profile
        for name in ["address", "passport_data"]:
            self.fields[name].initial = getattr(profile, name, None)

    def clean_bank(self):
        currency, bank = (self.cleaned_data["currency"],
                          self.cleaned_data["bank"])
        name, swift = settings.BANK_ACCOUNTS.get(currency)[int(bank)]
        return name

    @staticmethod
    def get_bank_base(account):
        return settings.BANKS['Verso']

    def get_bank(self):
        return self.get_bank_base(self.cleaned_data["account"])

    def clean(self):
        if "bank" in self.cleaned_data:
            currency = self.cleaned_data["currency"]
            bank = self.cleaned_data["bank"]
            self.cleaned_data["swift"] = dict(settings.BANK_ACCOUNTS.get(currency))[bank]

        # Purse is calculated as a hash of all submitted fields.
        self.cleaned_data["purse"] = md5("%r" % self.cleaned_data).hexdigest()

        return super(DepositForm, self).clean()


class DetailsForm(base.DetailsForm, FormWithCountry, FormWithCity):

    address = forms.CharField(label=_("Beneficiary address"), help_text=_("Your city and street address"))
    bank = forms.CharField(label=_("Beneficiary Bank"), help_text=_("Your bank's name"))
    bank_account = forms.RegexField(label=_("Beneficiaries Account Number"), min_length=6,
                                    max_length=34, regex=r"^[\d\s\w]+$",
                                    help_text=_("Enter up to 34 symbols"),
                                    error_messages={"invalid": _("Incorrect IBAN")})  # IBAN
    bank_swift = forms.RegexField(label=_("Beneficiary Bank's Code"),
                                  max_length=11, regex="^[A-Za-z]{6}[A-Za-z0-9]{2}([A-Za-z0-9]{3})?$",
                                  help_text=_("SWIFT code. Enter up to 11 symbols"),
                                  error_messages={"invalid": _("Incorrect SWIFT code")})  # SWIFT
    bank_correspondent = forms.CharField(label=_("Correspondent bank"), help_text=_("Correspondent bank's name"), required=False)
    bank_correspondent_swift = forms.RegexField(label=_("Correspondent Bank's Code"), required=False,
                                  max_length=11, regex="^[A-Za-z]{6}[A-Za-z0-9]{2}([A-Za-z0-9]{3})?$",
                                  help_text=_("Correspondent bank SWIFT code. Enter up to 11 symbols"),
                                  error_messages={"invalid": _("Incorrect SWIFT code")})  # SWIFT

    def __init__(self, *args, **kwargs):
        super(DetailsForm, self).__init__(*args, **kwargs)

        del self.fields["purse"]

    def get_purse_field_name(self):
        return "bank_account"

    def clean(self):
        super(DetailsForm, self).clean()

        value_raw = self.cleaned_data.get("bank_account", "").upper()
        value = "".join(re.compile("[\d\w]+").findall(value_raw))

        is_iban = lambda account: account[:2].isalpha()

        # если первых два символа это буквы, то это IBAN и проводится валидация.
        # иначе это счет в российском банке и номер не проверяется, кроме как на число символов
        # (к этому моменту уже проверено через min_length)
        if is_iban(value):
            country = Country.objects.get(id=self.cleaned_data["country"])

            if not country.code in IBAN_COUNTRIES_CODES:
                self.errors["bank_account"] = _("Your country is not using IBAN codes")
            if not validate_iban(value):
                self.errors["bank_account"] = _("Not valid bank account")

        if "bank_account" in self.cleaned_data:
            self.cleaned_data["purse"] = self.cleaned_data["bank_account"]

        return self.cleaned_data


class WithdrawForm(base.WithdrawForm):
    info = _("bankbase.withdraw.info")


# Helpers.
def clean_translify(form):
    """Iterates over form fields and traslifies values."""
    for field, value in form.cleaned_data.iteritems():
        if not value or not isinstance(value, basestring):
            # Not a string field or empty? not interested ...
            continue

        if not field in form.errors:
            try:
                form.cleaned_data[field] = translify(force_unicode(value))
            except ValueError:
                # We'll better pass than leave user with a stupid error
                pass

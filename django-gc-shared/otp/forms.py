# -*- coding: utf-8 -*-

from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from geobase.phone_code_widget import CountryPhoneCodeFormField


class PhoneForm(forms.Form):
    phone_mobile = CountryPhoneCodeFormField(label=_("Phone number"),
                                             help_text=_("Enter your phone number"))

    def __init__(self, number=None, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs)
        if number:
            self.fields["phone_mobile"].initial = number


class OTPForm(forms.Form):
    token = forms.CharField(max_length=20, label=_("Token"), help_text=_("Token from your auth app"))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.user = kwargs.pop("user")
        self.auth_scheme = self.user.profile.auth_scheme

        super(OTPForm, self).__init__(*args, **kwargs)

    def clean_token(self):
        token = self.cleaned_data["token"]

        if not self.user.profile.otp_device.verify_token(token, self.request):
            raise ValidationError(_("Wrong token"))

        return token


class SMSForm(forms.Form):
    token = forms.CharField(max_length=20, label=_("Token"), help_text=_("Token send by SMS"))

    class Media:
        js = ("js/otp/send_sms.js",)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request")
        self.user = kwargs.pop("user")
        self.auth_scheme = self.user.profile.auth_scheme

        super(SMSForm, self).__init__(*args, **kwargs)

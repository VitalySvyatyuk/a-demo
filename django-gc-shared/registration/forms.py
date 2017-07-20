# coding=utf-8

import phonenumbers
from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from geobase.phone_code_widget import CountryPhoneCodeFormField
from geobase.utils import get_geo_data
from profiles.models import UserProfile
from profiles.validators import is_partner_account, latin_chars_name
from sms import send


class ProfileRegistrationForm(forms.Form):
    first_name = forms.CharField(label=_("First name"), max_length=30,
                                 required=True,
                                 validators=[latin_chars_name],
                                 help_text=_('Please use Engilsh only'))
    last_name = forms.CharField(label=_("Last name"), max_length=30,
                                required=True,
                                validators=[latin_chars_name],
                                help_text=_('Please use Engilsh only'))
    phone_mobile = CountryPhoneCodeFormField(label=_('Mobile phone'),
                                             required=True,
                                             help_text=_("Your password will be sent to you by SMS"))
    email = forms.EmailField(label=_("E-mail"),
                             error_messages={"invalid": _(u"Enter a valid Email address")},)
    agent_code = forms.IntegerField(label=_('Agent code'), required=False,
                                    help_text=_('If you don\'t know what it is, leave empty'),
                                    validators=[is_partner_account])
    is_adult = forms.BooleanField(label=_("I am over 18 years old"), required=True)
    registered_from = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProfileRegistrationForm, self).__init__(*args, **kwargs)

        if self.request and self.request.method == 'GET' and self.request.user.is_anonymous\
                and self.request.GET.get('email'):
            self.fields['email'].initial = self.request.GET['email']

        if self.request:
            geo_data = get_geo_data(self.request)
            if geo_data['country'] and geo_data['country'].phone_code:
                self.fields['phone_mobile'].initial = str(geo_data['country'].phone_code)

        for field in self:
            field.field.widget.attrs.update({"autocomplete": "off"})

    def clean(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """

        registered_from = self.cleaned_data.get('registered_from', '')

        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email'].strip()
            if User.objects.filter(
                    email__iexact=email,
                    profile__registered_from=registered_from
            ).exists():
                raise forms.ValidationError(mark_safe(_("Email you provided is already registered in our system.<br/>\
    If you forgot the password, please visit <a href='%(recovery)s'>the password recovery page</a>.<br/>\
    If you remember your password, use it to log in to your <a href='%(private_office)s'>Private Office</a>") % {
                    'recovery': reverse('password_reset'),
                    'private_office': reverse('auth_login'),
                }))

        if 'phone_mobile' in self.cleaned_data:
            phone_mobile = self.cleaned_data['phone_mobile'].strip()
            if phone_mobile and phone_mobile[0] == '8':
                phone_mobile = "+7" + phone_mobile[1:]
            if User.objects.filter(
                    profile__phone_mobile=phone_mobile,
                    profile__registered_from=registered_from
            ).exists():
                self.data = self.data.copy()  # To make it mutable
                self.data['phone_mobile'] = phone_mobile
                raise forms.ValidationError(mark_safe(_("Mobile phone you provided is already registered in our system.<br/>\
    If you forgot the password, please visit <a href='%(recovery)s'>the password recovery page</a>.<br/>\
    If you remember your password, use it to log in to your <a href='%(private_office)s'>Private Office</a>") % {
                    'recovery': reverse('password_reset'),
                    'private_office': reverse('auth_login'),
                }))
            else:
                self.cleaned_data['phone_mobile'] = phone_mobile

        geo_data = get_geo_data(self.request)

        return self.cleaned_data


class ShortLandingProfileRegistrationForm(forms.Form):
    first_name = forms.CharField(label=_("First name"), max_length=30, required=True)
    phone_mobile = forms.CharField(label=_('Mobile phone'), max_length=20, required=True)
    email = forms.EmailField(label=_("E-mail"),
                             error_messages={"invalid": _(u"Enter a valid Email address")}, )
    is_adult = forms.BooleanField(label=_("I am over 18 years old"), required=True)
    registered_from = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ShortLandingProfileRegistrationForm, self).__init__(*args, **kwargs)

    def clean(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        if 'email' in self.cleaned_data:
            email = self.cleaned_data['email'].strip()
            if User.objects.filter(
                    email__iexact=email,
                    profile__registered_from=self.cleaned_data['registered_from']
            ).exists():
                self.add_error('email', forms.ValidationError(mark_safe(_("Email you provided is already registered in our system.<br/>\
        If you forgot the password, please visit <a href='%(recovery)s'>the password recovery page</a>.<br/>\
        If you remember your password, use it to log in to your <a href='%(private_office)s'>Private Office</a>") % {
                    'recovery': reverse('password_reset'),
                    'private_office': reverse('auth_login'),
                })))

        if 'phone_mobile' in self.cleaned_data:
            phone_mobile = self.cleaned_data['phone_mobile']
            geo_data = get_geo_data(self.request) if self.request else {}
            country = geo_data.get("country")
            country = country.code if country else None
            phone_number = None
            try:
                phone_number = phonenumbers.parse(phone_mobile, country)
            except phonenumbers.NumberParseException:
                pass
            if not (phone_number and phonenumbers.is_valid_number(phone_number)):
                self.add_error('phone_mobile',
                               forms.ValidationError(_(u"Please enter your phone number in international format")))
            if phone_number:
                phone_mobile = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            self.data = self.data.copy()
            self.data['phone_mobile'] = phone_mobile
            if UserProfile.objects.filter(phone_mobile=phone_mobile, registered_from="").exists():
                self.data = self.data.copy()  # To make it mutable
                self.data['phone_mobile'] = phone_mobile
                self.add_error('phone_mobile', forms.ValidationError(mark_safe(_("Mobile phone you provided is already registered in our system.<br/>\
            If you forgot the password, please visit <a href='%(recovery)s'>the password recovery page</a>.<br/>\
            If you remember your password, use it to log in to your <a href='%(private_office)s'>Private Office</a>") % {
                    'recovery': reverse('password_reset'),
                    'private_office': reverse('auth_login'),
                })))
            else:
                self.cleaned_data['phone_mobile'] = phone_mobile
        return self.cleaned_data


class LandingProfileRegistrationForm(ProfileRegistrationForm):

    error_css_class = 'errors'

    def __init__(self, *args, **kwargs):
        super(LandingProfileRegistrationForm, self).__init__(*args, **kwargs)

        for field_name in ["first_name", "last_name", "phone_mobile", "email"]:
            field = self.fields[field_name]
            field.widget.attrs.update({"placeholder": field.label})

    def clean(self):
        super(LandingProfileRegistrationForm, self).clean()

        for field_name in ["first_name", "last_name", "email", "phone_mobile"]:
            field = self.fields[field_name]
            field_errors = self.errors.get(field_name)
            if field_errors:
                field.widget.attrs["title"] = "<br>".join(field_errors)
                field.widget.attrs["class"] = field.widget.attrs.get("class", "") + " errors"

        return self.cleaned_data


class EmailAuthenticationForm(forms.Form):
    email_phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'maxlength': 75}),
        label=_('Login, E-mail or Mobile phone')
    )
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    remember = forms.BooleanField(label=_("Remember me"), required=False,
                                  help_text=_("Check this if you want to stay "
                                              "logged in for the next %s days"))
    login_from = forms.CharField(widget=forms.HiddenInput(), required=False)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super(EmailAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields["remember"].help_text %= settings.LOGIN_FOR

    def clean(self):
        # No point of authenticating when any of the fields already
        # has errors.
        if "email_phone" in self.errors or "password" in self.errors:
            return self.cleaned_data

        self.user_cache = authenticate(
            email_phone=self.cleaned_data["email_phone"].strip(),
            password=self.cleaned_data["password"].strip(),
            login_from=self.cleaned_data["login_from"])

        if not self.user_cache:
            self.errors["__all__"] = self.error_class([
                _(u"Please enter correct login, e-mail address or mobile phone and password. "
                  u"Note that password is case-sensitive.")])
        elif not self.user_cache.is_active and\
            (datetime.now() - self.user_cache.date_joined) > timedelta(settings.ACCOUNT_ACTIVATION_DAYS):
            # The user didn't activate his account during the ACCOUNT_ACTIVATION_DAYS period
            self.errors["email"] = self.error_class(
                [_("This account is inactive.")])
        return self.cleaned_data

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache


class PasswordResetByPhoneForm(forms.Form):
    phone = forms.CharField(
        widget=forms.TextInput(
            attrs={'maxlength': 75}),
        label=_("Mobile phone"),
        help_text='+79291234567'
    )

    def send_new_password_by_sms(self):
        profiles = UserProfile.objects.filter(phone_mobile=self.cleaned_data["phone"])
        if len(profiles) == 1:
            user = profiles[0].user
            password = User.objects.make_random_password()
            user.set_password(password)
            user.save()
            text = _(u"Your new password: %s") % password
            send(to=self.cleaned_data["phone"], text=text)


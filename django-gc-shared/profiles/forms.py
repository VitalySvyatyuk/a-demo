# -*- coding: utf-8 -*-

import re

from django import forms
from django.forms.forms import BoundField
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language
from django.forms.widgets import CheckboxSelectMultiple

from notification import models as notification
from log.models import Logger, Events, Event
from profiles.validators import is_partner_account
from shared.werkzeug_utils import cached_property
from geobase.models import Country
from profiles.models import UserProfile, UserDocument, get_validation, DOCUMENTS
from shared.widgets import DateWidget


def check_extensions(file):
    if not re.search('\.(%s)' % '|'.join(DocumentForm.EXTENSIONS), file.name.lower()):
        raise forms.ValidationError(_('Unsupported file extension'))
    if file.size > DocumentForm.FILESIZE_LIMIT:
        raise forms.ValidationError(_('File is too big.'))
    return file


class ValidatedField(BoundField):
    """A field which knows it's validation status."""

    @cached_property
    def status(self):
        return get_validation(self.form.instance.user, self.name)


class DocumentForm(forms.ModelForm):
    FILESIZE_LIMIT = 1024 ** 2 * 5
    EXTENSIONS = ('doc', 'docx', 'bmp', 'gif', 'jpg', 'jpeg', 'png', 'pdf')

    def __init__(self, *args, **kwargs):
        available_documents = kwargs.pop("documents", None)
        super(DocumentForm, self).__init__(*args, **kwargs)
        self.fields['file'].help_text = _('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb') % {
            'ext': ', '.join(self.EXTENSIONS),
            'limit': '%.2f' % (self.FILESIZE_LIMIT / 1024.0 / 1024)
        }
        self.fields["file"].validators = [check_extensions]

        if available_documents:
            self.fields["name"].choices = [(k, DOCUMENTS[k]) for k in available_documents]

    class Meta:
        model = UserDocument
        exclude = ['user', 'is_deleted']


class AvatarUploadForm(forms.ModelForm):
    FILESIZE_LIMIT = 1024 ** 2 * 5
    EXTENSIONS = ('gif', 'jpg', 'jpeg', 'png')

    def __init__(self, *args, **kwargs):
        super(AvatarUploadForm, self).__init__(*args, **kwargs)
        self.fields['avatar'].help_text = _('Supported extensions: %(ext)s. Filesize limit: %(limit)s Mb') % {
            'ext': ','.join(self.EXTENSIONS),
            'limit': '%.2f' % (self.FILESIZE_LIMIT / 1024.0 / 1024)
        }
        self.fields["avatar"].validators = [check_extensions]

    class Meta:
        model = UserProfile
        fields = "avatar",


class ProfileForm(forms.ModelForm):
    username = forms.RegexField(regex=r'^[a-z\._A-Z0-9]+$',
                                label=_('Forum username'),
                                help_text=_('Your username on the forum,'
                                            ' only english letters, numbers or underscores allowed'))
    first_name = forms.CharField(label=_("First name"), max_length=30,
                                 required=False)
    last_name = forms.CharField(label=_("Last name"), max_length=30,
                                required=False)
    middle_name = forms.CharField(label=_("Middle name"), max_length=45,
                                  required=False)
    email = forms.EmailField(label=_("e-mail address"), required=False)
    icq = forms.IntegerField(label=_("ICQ"), required=False,
                             error_messages={"invalid": _(u"Enter a valid ICQ number.")},
                             help_text=_("Example: 629301132"))
    skype = forms.CharField(label=_("Skype"), required=False,
                            error_messages={"invalid": _(u"Enter a valid Skype account.")},
                            help_text=_("Example: gc_clients"))
    birthday = forms.DateField(label=_('Birthday'), required=False, widget=DateWidget(),
                               help_text=_('Example: 28.12.1987'))
    country = forms.ModelChoiceField(label=_('Country'), required=False,
                                     queryset=Country.objects.exclude(code__in=('US', 'GB')))

    class Meta:
        model = UserProfile
        fields = ("username", "first_name", "last_name", "middle_name",
                  "birthday", "country", "state", "city", "address", "email",
                  "skype", "icq", "phone_home", "phone_work", "phone_mobile",
                  "tin", "social_security", "agent_code",)

    def __init__(self, *args, **kwargs):

        self.request = kwargs.pop("request")

        super(ProfileForm, self).__init__(*args, **kwargs)

        if 'subscription' in self.fields:
            self.fields['subscription'].help_text = _('You will receive the subscriptions\
                you select to your e-mail and via text messages on your phone')
        if get_language() != "ru":
            del self.fields['middle_name']

        try:
            # FIXME: an ugly hack, populating User attributes with inital
            # data. Probably it's best to make a separate form for them.
            for field in ("first_name", "last_name", "email", "username"):
                self[field].field.initial = getattr(self.instance.user, field)
        except User.DoesNotExist:
            # Occurs only in the testing environment, when no Users are
            # present in the database.
            return

        def clean_validated_field(field_name):
            def inner():
                initial = (getattr(self.instance, field_name, None)
                           or getattr(self.instance.user, field_name, None))

                value = self.cleaned_data[field_name]

                # you cannot change phone number via profile edit if you have sms-binding
                if field_name == "phone_mobile":
                    if self.instance.user.profile.auth_scheme == "sms":
                        return initial
                    value = "".join(c for c in value if c in '1234567890+')

                if value != initial:
                    # Removing Validation object for that field, if the value has changed.
                    self.instance.user.validations.filter(key=field_name).delete()
                    Logger(user=self.request.user, content_object=self.request.user.profile,
                           ip=self.request.META["REMOTE_ADDR"], event=Events.VALIDATION_REVOKED,
                           params={"field": field_name}).save()
                return value

            return inner

        if self.instance.agent_code:
            del self.fields["agent_code"]
        else:
            self.fields["agent_code"].validators = [is_partner_account]

        # Fetching all validated fields from the database and
        # adding clean_*() methods for each of them, to prevent
        # the user from changing them.
        for field_name in self.instance.user.validations.filter(is_valid=True).values_list("key", flat=True):
            setattr(self, "clean_%s" % field_name, clean_validated_field(field_name))

        # As soon as we pass the profile data to the trade server,
        # and it accepts cp1251 encoding, we should check that the profile
        # data does not contain any symbols, which cannot be encoded into
        # cp1251
        def encoding_validator(encoding):
            def is_encodable(value):
                try:
                    unicode(value).encode(encoding)
                except UnicodeEncodeError:
                    raise forms.ValidationError(_('Illegal symbols'))
                return value

            return is_encodable

        for field in self.fields.values():
            field.validators.append(encoding_validator('cp1251'))

    def __iter__(self):
        for name, field in self.fields.items():
            yield ValidatedField(self, field, name)

    def clean(self):
        if (self.cleaned_data.get('username')
            and self.instance.user.username != self.cleaned_data['username']
            and User.objects.filter(username=self.cleaned_data['username']).exists()):
            self._errors['username'] = [_('This username already exists')]
        return self.cleaned_data

    def clean_phone_mobile(self):
        instance = getattr(self, 'instance', None)
        if instance and instance.pk and instance.user.profile.auth_scheme == "sms":
            return instance.phone_mobile
        else:
            return self.cleaned_data['phone_mobile']

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        """
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError(_("Email you provided is already registered in our system."))
        return email

    def save(self, **kwargs):
        profile = super(ProfileForm, self).save(**kwargs)

        #update user instance fields
        try:
            # Updating related User object. A better solution?
            for field in ("username", "first_name", "last_name", "email"):
                setattr(self.instance.user, field, self.cleaned_data[field])
                self.instance.user.save()
        finally:
            return profile


class BriefProfileForm(ProfileForm):
    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "middle_name", "country", "state",
                  "city", "address", "email", "phone_mobile", "agent_code")

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(BriefProfileForm, self).__init__(*args, **kwargs)

        del (self.fields['username'])

        # If we process an anonymous request, we'll have an email field
        # on the RegistrationForm, so we can remove it from this one,
        # see mt4/onestep.py for details.
        if self.request and self.request.user.is_anonymous():
            del self.fields["email"]
            # The agent_code removing code from ProfileForm does not work
            # here, so we should define this case explicitly.
            if 'agent_code' in self.request.session:
                self.agent_code = self.request.session['agent_code']
                del (self.fields['agent_code'])

        # Removing extra fields added explicitly in ProfileForm.
        for field in ("skype", "icq", "birthday"):
            del self.fields[field]

        # All fields except are required for this form.
        for field in (f for f in self if f.name not in ['agent_code']):
            field.field.required = True

        if self.request and self.request.META['REMOTE_ADDR']:
            self.fields['country'].initial = Country.objects.get_by_ip(self.request.META['REMOTE_ADDR'])

        if self.request and self.request.method == 'GET':
            if self.request.GET.get('first_name'):
                self.fields['first_name'].initial = self.request.GET.get('first_name')
            if self.request.GET.get('last_name'):
                self.fields['last_name'].initial = self.request.GET.get('last_name')
                #if self.request.GET.get('email'):
            #    self.fields['email'].initial = self.request.GET.get('email')
            if self.request.GET.get('phone'):
                self.fields['phone_mobile'].initial = self.request.GET.get('phone')

    def save(self, **kwargs):
        try:
            self.instance.agent_code = self.agent_code
        except AttributeError:
            pass
        return super(BriefProfileForm, self).save(**kwargs)


class EmailProfileForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'maxlength': 75}),
                             label=_('E-mail address'), required=True)

    class Meta:
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super(EmailProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].help_text = _('Account activation link will\
         be sent to this e-mail address.')


class ActionProfileForm(BriefProfileForm):
    def __init__(self, *args, **kwargs):
        super(ActionProfileForm, self).__init__(*args, **kwargs)

        if 'middle_name' in self.fields:
            del (self.fields['middle_name'])

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "country",
                  "state", "email", "phone_mobile", "agent_code")


class UserPasswordForm(forms.Form):


    old = forms.CharField(required=True)
    new = forms.CharField(required=True)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserPasswordForm, self).__init__(*args, **kwargs)

    def clean_old(self):
        data = self.cleaned_data['old']
        if not self.user.check_password(data):
            Event.PASSWORD_CHANGE_FAIL.log(self.user)
            raise forms.ValidationError(_("Wrong password"))
        return data

    def save(self):
        self.user.set_password(self.cleaned_data['new'])
        self.user.save()
        notification.send([self.user], 'Password_changed')
        Event.PASSWORD_CHANGE_OK.log(self.user)

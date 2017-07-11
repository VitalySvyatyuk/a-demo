# -*- coding: utf-8 -*-
import re
from collections import OrderedDict
from datetime import date

from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.postgres.fields import HStoreField

from profiles.models import UserProfile, UserDocument
from profiles.validators import latin_chars_name, latin_chars_name_with_numbers

from platforms.models import TradingAccount
from geobase.rest_fields import PhoneField



def is_valid_in_encoding(encoding, value):
    try:
        unicode(value).encode(encoding)
    except UnicodeEncodeError:
        return False
    return True


#temporary fix for custom fields
from geobase.phone_code_widget import CountryPhoneCodeField
serializers.ModelSerializer.serializer_field_mapping[CountryPhoneCodeField] = serializers.CharField


class UserProfileSerializer(serializers.ModelSerializer):
    is_phone_mobile_valid = serializers.ReadOnlyField(source='has_valid_phone')
    phone_mobile = PhoneField(label=_("Mobile phone"))
    otp_type = serializers.SerializerMethodField()
    status_info = serializers.SerializerMethodField()

    @staticmethod
    def can_change_profile_data(obj):
        """ Return true if we allowing user to change his personal data"""

        return obj.status < UserProfile.NO_DOCUMENTS and not UserDocument.objects.filter(user=obj.user).exists()


    def get_otp_type(self, obj):
        if obj.otp_device:
            return obj.otp_device.type.lower()

    def get_status_info(self, obj):
        return {"code": obj.status, "display": obj.STATUSES[obj.status],
                "verified": True if obj.status == UserProfile.VERIFIED else False,
                "sended_docs": not UserProfileSerializer.can_change_profile_data(obj)
                }

    def validate_phone_mobile(self, value):
        if value != self.instance.phone_mobile:
            if self.instance.auth_scheme == "sms":
                raise serializers.ValidationError(_("Cannot edit mobile phone number because it is binded for OTP"))
            elif UserProfile.objects.filter(phone_mobile__iexact=value).exists():
                phone_mobile = value.strip()
                if phone_mobile and phone_mobile[0] == '8':
                    phone_mobile = "+7" + phone_mobile[1:]
                if UserProfile.objects.filter(
                    phone_mobile=phone_mobile,
                    registered_from=self.instance.registered_from,
                ).exists():
                    raise serializers.ValidationError(_("Mobile phone you provided is already registered in our system."))
        return value

    def validate_middle_name(self, value):
        if value:
            latin_chars_name(value)
        return value

    def validate_city(self, value):
        if value:
            latin_chars_name(value)
        return value

    def validate_address(self, value):
        if value:
            latin_chars_name_with_numbers(value)
        return value


    def validate_birthday(self, value):
        today = date.today()
        if today.year - value.year - ((today.month, today.day) < (value.month, value.day)) < 18:
            raise serializers.ValidationError(_('Only persons of legal age can be the clients of ARUM CAPITAL'))
        return value

    def validate_agent_code(self, value):
        # TODO: rewrite as read-only field
        if self.instance.agent_code:
            if self.instance.agent_code != value:
                raise serializers.ValidationError(_("Cannot edit partner code"))
            return value

        if value:
            try:
                TradingAccount.objects.real_ib().get(mt4_id=value)
            except (TradingAccount.DoesNotExist, ValueError):
                raise serializers.ValidationError(_("Wrong partner code"))
            except TradingAccount.MultipleObjectsReturned:
                pass
        return value

    def validate_education_level(self, value):
        if not value:
            raise serializers.ValidationError(_("Please fill this field"))
        return value

    def validate_nature_of_biz(self, value):
        if not value:
            raise serializers.ValidationError(_("Please fill this field"))
        return value

    def validate_source_of_funds(self, value):
        if not value:
            raise serializers.ValidationError(_("Please fill this field"))
        return value

    def validate(self, data):
        for f, v in data.iteritems():
            if isinstance(v, (str, unicode)) and not is_valid_in_encoding('cp1251', v):
                raise serializers.ValidationError({f: _("Illegal symbols")})
        return data

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'middle_name',
            'birthday',

            'country',
            'nationality',
            'is_russian',
            'city',
            'state',
            'address',
            'net_capital',
            'annual_income',
            'tin',
            'tax_residence',
            'us_citizen',
            'employment_status',
            'source_of_funds',
            'nature_of_biz',
            'financial_commitments',
            'phone_mobile',
            'is_phone_mobile_valid',
            'avatar',
            'manager',
            'purpose',
            'account_turnover',

            'investment_undertaking',
            'derivative_instruments',
            'forex_instruments',
            'transferable_securities',
            'education_level',


            'agent_code',
            'lost_otp',
            'otp_type',

            'subscription',

            'has_valid_documents',
            'status_info',
            'email_verified',
            "is_partner",
        )
        read_only_fields = (
            'avatar',
            'has_valid_documents',
            'manager',
            'lost_otp',
            'is_partner'
        )


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()
    first_name = serializers.CharField(label=_("First name"), required=True, validators=[latin_chars_name])
    last_name = serializers.CharField(label=_("Last name"), required=True, validators=[latin_chars_name])

    # username = serializers.RegexField(
    #     label=_(u"username"),
    #     regex=r'^[a-z\._A-Z0-9]+$',
    #     help_text=_(u"Your username on the forum, only english letters, numbers or underscores allowed"))

    def __init__(self, instance=None, *a, **kwa):
        instance_profile = instance
        if instance:
            instance_profile = instance.profile
        self.fields['profile'] = UserProfileSerializer(instance=instance_profile, *a, **kwa)
        return super(UserSerializer, self).__init__(instance=instance, *a, **kwa)

    def validate_username(self, value):
        pattern = r'^[a-z\._A-Z0-9]+$'
        if re.match(pattern, value) is None:
            raise serializers.ValidationError(_('Only english letters, numbers or underscores allowed'))
        elif value != self.instance.username:
                if User.objects.filter(username__iexact=value).exists():
                    raise serializers.ValidationError(_('This username already exists'))
        return value

    def validate_email(self, value):

        if value != self.instance.email:
            if User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError(_("Email you provided is already registered in our system."))
        else:
            user = User.objects.filter(email__iexact=value)
            if not UserProfile.objects.filter(user=user, email_verified=True):
                raise serializers.ValidationError(_("Please confirm Email"))
        return value


    def validate(self, attrs):
        # req = self.context['request']
        profile = UserProfile.objects.get(user__username=self.instance.username)


        # We dont need to check permission for change profile if user change only subscriptions
        subscriptions_changed = \
            set(self.instance.profile.subscription.values_list("pk", flat=True)) != \
            set([i.pk for i in attrs[u'profile'][u'subscription']])
        if subscriptions_changed:
            # Set rest profile fields to database value so it changes only subscription field
            for i in attrs[u'profile'].iterkeys():
                if i != u'subscription':
                    attrs[u'profile'][i] = getattr(self.instance.profile, i)
        else:
            if not UserProfileSerializer.can_change_profile_data(profile):
                raise serializers.ValidationError('Sorry we cant let you change your personal data now, '
                                              'complete the regitration process or contact with support')

        for f, v in attrs.iteritems():
            if isinstance(v, (str, unicode)) and not is_valid_in_encoding('cp1251', v):
                raise serializers.ValidationError({f: _("Illegal symbols")})
        return attrs

    def update(self, instance, validated_data):

        for attr, value in validated_data.pop('profile').items():
            setattr(instance.profile, attr, value)
        instance.profile.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',

            'profile',

            'is_superuser',
            'is_staff',
            'is_active',

            'groups',

            'last_login',
            'date_joined'
        )
        read_only_fields = (
            'is_superuser',
            'is_staff',
            'is_active',

            'groups',

            'last_login',
            'date_joined'
        )


class UserDocumentSerializer(serializers.ModelSerializer):
    name_display = serializers.ReadOnlyField(source='get_name_display')

    def __init__(self, *args, **kwargs):
        super(UserDocumentSerializer, self).__init__(*args, **kwargs)
        self.fields['file'].help_text = self.fields['file'].help_text % {
            'ext': ', '.join(UserDocument.EXTENSIONS),
            'limit': '%.2f' % (UserDocument.FILESIZE_LIMIT / 1024.0 / 1024)
        }

    class Meta:
        model = UserDocument
        fields = (
            'id',
            'name',
            'file',
            'name_display',
            'creation_ts',
            'fields'
        )
        extra_kwargs = {
                'file': {'write_only': True}
        }

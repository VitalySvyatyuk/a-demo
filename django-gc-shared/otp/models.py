# -*- coding: utf-8 -*-
import base64
import random
import urllib
from time import time

import requests
from annoying.decorators import signals
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _, get_language
from django_otp.models import Device
from django_otp.oath import totp

from geobase.phone_code_widget import CountryPhoneCodeField
from otp.utils import make_hash
from sms import send

AUTH_SCHEMES = (
    ("otp", "OTP auth"),
    ("sms", "SMS auth"),
    ("voice", "Voice auth"),
)


def random_base32(length=16, chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"):
    rand = random.SystemRandom()
    return ''.join(rand.choice(chars) for i in xrange(length))


class BaseDevice(Device):

    is_deleted = models.BooleanField(u"Is deleted?", default=False)

    class Meta:
        abstract = True


class OTPDevice(BaseDevice):
    type = "OTP"
    key = models.CharField(max_length=80, default=random_base32, help_text=u"A secret key")
    step = models.PositiveSmallIntegerField(default=30, blank=True, help_text=u"The time step in seconds.")
    t0 = models.BigIntegerField(default=0, blank=True, help_text=u"The Unix time at which to begin counting steps.")
    digits = models.PositiveSmallIntegerField(choices=[(6, 6), (8, 8)], default=6, blank=True,
                                              help_text=u"The number of digits to expect in a token.")
    tolerance = models.PositiveSmallIntegerField(default=1, blank=True,
                                                 help_text=u"The number of time steps in the "
                                                           u"past or future to allow.")
    drift = models.SmallIntegerField(default=0, blank=True,
                                     help_text=u"The number of time steps the prover "
                                               u"is known to deviate from our clock.")
    creation_ts = models.DateTimeField(u"Added at", auto_now_add=True)

    class Meta():
        db_table = "profiles_otpdevice"
        verbose_name = u"OTP device"
        verbose_name_plural = u"OTP devices"

    @staticmethod
    def generate_token():
        return ""

    def verify_token(self, token, request):
        try:
            token = int(token)
        except StandardError:
            verified = False
        else:
            key = self.bin_key

            for offset in range(-self.tolerance, self.tolerance + 1):
                if totp(key, self.step, self.t0, self.digits, self.drift + offset) == token:
                    verified = True
                    break
            else:
                verified = False

        return verified

    def uri(self, name, scheme="totp"):
        return u'otpauth://%(scheme)s/%(name)s?secret=%(secret)s' % {
            'name': urllib.quote(name.encode("utf-8"), safe='@'),
            'secret': self.key,
            'scheme': scheme,
        }

    def initiate(self, data):
        """
        `data` -- data to sign with token
        returns tuple:
            `hash` -- should be remembered for next step
            `hashed_at` -- timestamp, at which hash was created
        """
        hashed_at = int(time())
        otp_hash = make_hash('totp', data, self.key, unicode(hashed_at))
        return otp_hash, hashed_at

    def verify_token_and_data(self, token, data, hashed_at, otp_hash):
        """
        `token` -- user input
        `data` -- signed data from `initiate`
        `hashed_at` -- hashed at
        `otp_hash` -- hash from `initiate`
        """
        return self.verify_token(token, None) \
            and (make_hash('totp', data, self.key, unicode(hashed_at)) == otp_hash)

    @property
    def bin_key(self):
        return base64.b32decode(self.key, casefold=True)

    def __unicode__(self):
        return "OTPDevice: %s owned by %s" % (self.name, self.user)


@signals.post_save(sender=OTPDevice)
def on_otpdevice_save(sender, instance, *args, **kwargs):
    instance.user.profile.auth_scheme = "otp"
    instance.user.profile.save()

    if not instance.name:
        instance.name = "OTP"
        instance.save()


@signals.post_delete(sender=OTPDevice)
def on_otpdevice_delete(sender, instance, *args, **kwargs):
    from profiles.models import UserProfile
    try:
        # will fail if user has been deleted already
        instance.user.profile.auth_scheme = None
        instance.user.profile.save()
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        pass


class SMSDevice(BaseDevice):
    type = "SMS"
    creation_ts = models.DateTimeField(u"Added at", auto_now_add=True)
    phone_number = CountryPhoneCodeField("Phone", max_length=40, null=True)

    class Meta():
        db_table = "profiles_smsdevice"
        verbose_name = "SMS Device"
        verbose_name_plural = "SMS Devices"

    def deliver_token(self, token=None):
        if token is None:
            token = self.generate_token()
        return send(self.phone_number, self.get_sms_text(token))

    @staticmethod
    def generate_token():
        return ''.join(random.choice('0123456789') for i in range(6))

    @staticmethod
    def get_sms_text(token):
        return _(u"Your code: %s \n\nPlease enter it in the verification field.") % token

    @staticmethod
    def send_sms(to, text=None, token=None):
        from sms import send
        return send(to=to, text=text or SMSDevice.get_sms_text(token or SMSDevice.generate_token()))

    def verify_token(self, token, request):
        from otp.forms import PhoneForm
        from otp.views import make_hash

        token = request.POST.get("sms_check", "")
        form = PhoneForm(data=request.POST)

        if not form.is_valid():
            return False

        phone_number = form.cleaned_data["phone_mobile"]
        old_hash = request.POST.get("preview_hash", "")

        extra_fields = {
            "token": token,
            "phone_mobile": phone_number
        }

        return make_hash(extra_fields, target="preview") == old_hash

    def initiate(self, data):
        """
        `data` -- data to sign with token
        returns tuple:
            `otp_hash` -- should be remembered for next step
            `hashed_at` -- timestamp, at which hash was created
        """
        hashed_at = int(time())
        token = self.generate_token()
        otp_hash = make_hash(
            'sms', data, unicode(token), self.phone_number, unicode(hashed_at))

        #deliver token
        send(self.phone_number, self.get_sms_text(token))
        return otp_hash, hashed_at

    def verify_token_and_data(self, token, data, hashed_at, otp_hash):
        """
        `token` -- user input
        `data` -- signed data from `initiate`
        `hashed_at` -- hashed at
        `otp_hash` -- hash from `initiate`
        """
        return make_hash(
            'sms', data, unicode(token), self.phone_number, unicode(hashed_at)
        ) == otp_hash

    def get_voice_device(self):
        device = VoiceDevice()
        device.user = self.user
        device.phone_number = self.phone_number
        return device

    def __unicode__(self):
        return "SMSDevice: %s owned by %s" % (self.name, self.user)


@signals.post_save(sender=SMSDevice)
def on_smsdevice_save(sender, instance, *args, **kwargs):
    profile = instance.user.profile
    profile.auth_scheme = "sms"
    profile.save()

    if not instance.name:
        instance.name = "SMS"
        instance.save()


@signals.post_delete(sender=SMSDevice)
def on_smsdevice_delete(sender, instance, *args, **kwargs):
    from profiles.models import UserProfile
    try:
        # will fail if user has been deleted already
        instance.user.profile.auth_scheme = None
        instance.user.profile.save()
    except (User.DoesNotExist, UserProfile.DoesNotExist):
        pass


class VoiceDevice(BaseDevice):
    type = "voice"
    creation_ts = models.DateTimeField(u"Added at", auto_now_add=True)
    phone_number = None
    # TODO: update it
    # CountryPhoneCodeField("Phone", max_length=40, null=True)

    class Meta(Device.Meta):
        db_table = "profiles_voicedevice"
        verbose_name = "Voice Device"
        verbose_name_plural = "Voice Devices"

    @classmethod
    def deliver_token(cls, request, phone, token=None):
        if token is None:
            token = cls.generate_token()

        if request.user.profile.country:
            lang = request.user.profile.country.language
        else:
            lang = get_language()

        data = (
            "Channel: Local/%(phone)s@ExternalSets\n"
            "Callerid: 445455445\n"
            "Context: gc_saycode\n"
            "Extension: main\n"
            "Setvar: MYCODE=%(token)s\n"
            "Setvar: LANG=%(lang)s\n"
            "MaxRetries: 0\n"
            "Archive: Yes\n"
            "RetryTime: 60\n"
            "WaitTime: 60\n" % {
                "phone": phone.strip("+"),
                "token": token,
                "lang": lang,
            }
        )

        link = "%s_%s.call" % (request.user, int(time()))
        raise NotImplementedError("Soryan")

        return requests.put(link, data=data).status_code == 200

    @staticmethod
    def generate_token():
        return ''.join(random.choice('0123456789') for i in range(4))

    def __unicode__(self):
        return "VoiceDevice: %s owned by %s" % (self.name, self.user)

    def initiate(self, data):
        """
        `data` -- data to sign with token
        returns tuple:
            `otp_hash` -- should be remembered for next step
            `hashed_at` -- timestamp, at which hash was created
        """
        hashed_at = int(time())
        token = self.generate_token()
        otp_hash = make_hash(
            'voice', data, unicode(token), self.phone_number, unicode(hashed_at))

        if self.user.profile.country:
            lang = self.user.profile.country.language
        else:
            lang = get_language()

        callfile = (
            "Channel: Local/%(phone)s@ExternalSets\n"
            "Callerid: 2321\n"
            "Context: gc_saycode\n"
            "Extension: main\n"
            "Setvar: MYCODE=%(token)s\n"
            "Setvar: LANG=%(lang)s\n"
            "MaxRetries: 0\n"
            "RetryTime: 60\n"
            "Archive: Yes\n"
            "WaitTime: 60\n" % {
                "phone": self.phone_number.strip("+"),
                "token": token,
                "lang": lang,
            }
        )

        link = "%s_%s.call" % (
            self.user, hashed_at
        )
        raise NotImplementedError("Soryan")
        if settings.DEBUG:
            print 'OTP DEBUG VOICE: ', self.phone_number, token
        else:
            assert requests.put(link, data=callfile).status_code in [200, 201]
            # 200 - ok, 201 - created
        return otp_hash, hashed_at

    def verify_token_and_data(self, token, data, hashed_at, otp_hash):
        """
        `token` -- user input
        `data` -- signed data from `initiate`
        `hashed_at` -- hashed at
        `otp_hash` -- hash from `initiate`
        """
        return make_hash(
            'voice', data, unicode(token), self.phone_number, unicode(hashed_at)
        ) == otp_hash


@signals.post_save(sender=VoiceDevice)
def on_voicedevice_save(sender, instance, *args, **kwargs):
    if not instance.name:
        instance.name = "Voice"
        instance.save()


@signals.post_delete(sender=VoiceDevice)
def on_voicedevice_delete(sender, instance, *args, **kwargs):
    try:
        # will fail if user has been deleted already
        instance.user.profile.auth_scheme = None
        instance.user.profile.save()
    except User.DoesNotExist:
        pass


DEVICE_TYPES = (
    SMSDevice, OTPDevice, VoiceDevice
)

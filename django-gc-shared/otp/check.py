# -*- coding: utf-8 -*-
from time import time

from django.core.cache import cache
from rest_framework import exceptions
from rest_framework import status

from log.models import Event
from otp.utils import dict_without


class OTPTokenRequested(exceptions.APIException):
    status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
    default_detail = u'otp_requested'

    def __init__(self, data):
        self.data = data
        self.detail = {
            'detail': data
        }


class OTPDeviceRequired(exceptions.APIException):
    status_code = status.HTTP_511_NETWORK_AUTHENTICATION_REQUIRED
    default_detail = u'otp_required'


class NoDevice(Exception):
    pass


class OTPTokenNeeded(Exception):
    def __init__(self, data):
        self.data = data


class InvalidOTPToken(Exception):
    pass


def check_otp(action, user, input_data, secure_data=None, otp_device=None):
    if not (otp_device or user.profile.has_otp_devices):
        raise NoDevice()

    cache_key = "failed_otp_check_%d" % user.id
    fails = cache.get(cache_key) or 0
    if fails > 5:
        raise InvalidOTPToken()

    if not otp_device:
        otp_device = user.profile.otp_device

    otp_type = input_data.get(
        'otp_type',
        otp_device.type.lower()
    )

    if otp_type == 'voice' and otp_device.type.lower() == 'sms':
        otp_device = otp_device.get_voice_device()

    data = {
        'user_id': user.id,
        'action': action,

        #it is handy to provide just all data, so filter
        #some trashy from it
        'data': dict_without(
            input_data if secure_data is None else secure_data, [
                'otp_action_slug',
                'otp_hashed_at',
                'otp_token',
                'otp_hash',
                'otp_type'
            ])
    }

    #if we have no otp_hash, generate new one and send it back
    if 'otp_hash' not in input_data:
        otp_hash, otp_hashed_at = otp_device.initiate(data)
        raise OTPTokenNeeded({
            'otp_type': otp_type,
            'otp_hash': otp_hash,
            'otp_hashed_at': otp_hashed_at
        })
    else:
        if time() - int(input_data['otp_hashed_at']) >= 600:
            raise InvalidOTPToken()  # Token has expired. We will not log it.

        if not otp_device.verify_token_and_data(
            input_data.get('otp_token', None),
            data,
            input_data['otp_hashed_at'],
            input_data['otp_hash'],
        ):
            Event.OTP_FAIL.log(user, {
                'action': action,
                'device_type': otp_device.type,
                'device_key': getattr(otp_device, 'key', None),
                'device_phone_number': getattr(otp_device, 'phone_number', None),
            })
            cache.set(cache_key, fails + 1, 600)
            raise InvalidOTPToken()

    Event.OTP_OK.log(user, {
        'action': action,
        'device_type': otp_device.type,
        'device_key': getattr(otp_device, 'key', None),
        'device_phone_number': getattr(otp_device, 'phone_number', None),
    })


def check_otp_drf(action, request, secure_data=None, otp_device=None):
    try:
        check_otp(action, request.user, request.data, secure_data, otp_device)
    except NoDevice:
        raise OTPDeviceRequired()
    except OTPTokenNeeded as e:
        raise OTPTokenRequested(e.data)
    except InvalidOTPToken:
        raise exceptions.AuthenticationFailed(u'invalid_otp_token')

    #clean data
    finally:
        for i in [
            'otp_action_slug',
            'otp_hashed_at',
            'otp_token',
            'otp_hash',
            'otp_type'
        ]:
            if i in request.data:
                request.data.pop(i)


#verify requested type
def check_otp_old(action, request, otp_device=None, data=None):
    if not (otp_device or request.user.profile.has_otp_devices):
        raise exceptions.MethodNotAllowed(u'OTP device not found')

    otp_device = otp_device or request.user.profile.otp_device

    otp_type = request.data.get(
        'otp_type',
        otp_device.type.lower()
    )

    #if user requested voice one, override device with voice device
    if otp_type == 'voice' and otp_device.type.lower() == 'sms':
        otp_device = otp_device.get_voice_device()

    data = {
        'user_id': request.user.id,
        'path': request.path,
        'qs': request.QUERY_PARAMS,
        'data': data or dict_without(request.data, [
            'otp_hashed_at',
            'otp_token',
            'otp_hash',
            'otp_type'
        ])
    }

    if 'otp_token' not in request.data:
        otp_hash, otp_hashed_at = otp_device.initiate(data)
        raise OTPTokenRequested({
            'otp_type': otp_type,
            'otp_hash': otp_hash,
            'otp_hashed_at': otp_hashed_at
        })
    else:
        if not otp_device.verify_token_and_data(
            request.data['otp_token'],
            data,
            request.data['otp_hashed_at'],
            request.data['otp_hash'],
        ):
            raise exceptions.AuthenticationFailed(u'Invalid OTP token')

# coding=utf-8
import qrcode
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from log.models import Event
from otp.check import check_otp_drf, OTPTokenRequested
from otp.models import OTPDevice, random_base32
from otp.rest_serializers import SMSDeviceSerializer
from otp.utils import convert_to_base64


class OTPViewSet(viewsets.GenericViewSet):
    serializer_class = SMSDeviceSerializer
    paginator = None

    @list_route()
    def sms_data(self, request):
        from geobase.rest_fields import PhoneField
        return Response({
            'phone_number': PhoneField().metadata()
        })

    @list_route(methods=['post'])
    def bind(self, request):
        #create device
        # if we have any data to provide to user
        # in init - add to new_device_info
        secure_info = {}
        new_device_info = {}
        if request.data['type'] in ['sms', 'voice']:
            serializer = SMSDeviceSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=400)
            check_device = device = serializer.save()
            device.user = request.user
            secure_info['phone_number'] = device.phone_number
            if request.data['type'] == 'voice':
                check_device = device.get_voice_device()

        elif request.data['type'] == 'totp':
            check_device = device = OTPDevice(
                key=request.data.get('key', None) or random_base32(),
                user=request.user)
            uri_domain = u"%(name)s@%(debug)s%(domain)s" % {
                "debug": "debug." if settings.DEBUG else "",
                "name": request.user.username,
                "domain": settings.ROOT_HOSTNAME,
            }
            qr_img = qrcode.make(device.uri(uri_domain))

            new_device_info['qr'] = convert_to_base64(qr_img)
            new_device_info['key'] = secure_info['key'] = device.key
        else:
            raise NotImplementedError('...')

        if request.user.profile.has_otp_devices and 'verified' in request.data:
            request.data.pop('verified')
        else:
            try:
                check_otp_drf(
                    'Confirm new device', request, otp_device=check_device,
                    secure_data=secure_info)
            except OTPTokenRequested as e:
                e.data.update(new_device_info)
                raise e

        #finally, if user has prev device, request it
        if request.user.profile.has_otp_devices:
            check_otp_drf(
                'Replace device with new one', request,
                secure_data=secure_info)

        #then, save new device
        user_profile = request.user.profile
        user_profile.otp_devices.update(is_deleted=True)
        user_profile.lost_otp = False
        device.save()

        if device.type.lower() == 'sms':
            user_profile.phone_mobile = device.phone_number
            user_profile.make_valid("phone_mobile")

        user_profile.save()
        Event.OTP_BINDING_CREATED.log(request.user, {
            'device_type': device.type,
            'device_key': getattr(device, 'key', None),
            'device_phone_number': getattr(device, 'phone_number', None),
        })
        return Response(status=201)

# -*- coding: utf-8 -*-
from rest_framework import serializers
from geobase.rest_fields import PhoneField
from otp.models import SMSDevice


class SMSDeviceSerializer(serializers.Serializer):
    phone_number = PhoneField()

    def create(self, validated_data):
        return SMSDevice(**validated_data)

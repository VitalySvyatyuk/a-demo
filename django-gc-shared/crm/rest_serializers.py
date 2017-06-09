# -*- coding: utf-8 -*-

from __future__ import unicode_literals, division

from django.contrib.auth.models import User
from rest_framework import serializers

from crm.models import PersonalManager, RegionalOffice


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalOffice
        fields = (
            'id',
            'is_active',
            'slug',
            'name',
            'is_our',
        )


class ManagerSerializer(serializers.ModelSerializer):
    uid = serializers.ReadOnlyField(source='user_id')
    name = serializers.ReadOnlyField(source='user.profile.get_full_name')
    office = OfficeSerializer()

    class Meta:
        model = PersonalManager
        fields = (
            'id',
            'uid',
            'name',
            'office',
        )


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='profile.get_full_name')

    class Meta:
        model = User
        fields = (
            'id',
            'name',
        )

# -*- coding: utf-8 -*-
from rest_framework import serializers
from geobase.models import Country, Region


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = (
            'id',
            'name',
            'slug',
            'code',
            'weight',
            'phone_code',
            'is_primary',
            'phone_code_mask',
        )


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region

        fields = (
            'id',
            'country',
            'code',
            'name'
        )

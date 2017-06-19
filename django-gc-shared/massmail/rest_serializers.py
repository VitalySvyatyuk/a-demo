# -*- coding: utf-8 -*-
from rest_framework import serializers
from massmail.models import CampaignType


class CampaignTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CampaignType

        fields = (
            'id',
            'title',
        )

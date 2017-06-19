# -*- coding: utf-8 -*-
from rest_framework import serializers

from private_messages.models import Message


class MessageSerializer(serializers.ModelSerializer):
    new = serializers.ReadOnlyField()
    campaign = serializers.SerializerMethodField('get_campaign_info')

    def get_campaign_info(self, obj):
        return None

    class Meta:
        model = Message

        fields = (
            'id',

            'campaign',
            'subject',
            'body',

            'sender',

            'new',
            'sent_at',
            'is_html')

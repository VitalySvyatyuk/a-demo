# -*- coding: utf-8 -*-
from rest_framework import serializers

from private_messages.models import Message


class MessageSerializer(serializers.ModelSerializer):
    new = serializers.ReadOnlyField()
    campaign = serializers.SerializerMethodField('get_campaign_info')

    def get_campaign_info(self, obj):
        if obj.campaign:
            return {
                'id': obj.campaign.pk,
                'name': obj.campaign.email_subject,
                'url': obj.campaign.get_absolute_url()
            }

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

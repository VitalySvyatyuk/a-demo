# coding=utf-8

from rest_framework import serializers

from referral.models import PartnerDomain


class PartnerDomainSerializer(serializers.ModelSerializer):
    def validate_ib_account(self, value):
        acc = value
        if not (acc.user == self.context['request'].user and acc.is_ib):
            raise serializers.ValidationError("Access denied")
        return value

    class Meta:
        model = PartnerDomain
        fields = (
            'id',
            'api_key',
            'domain',
            'ib_account'
        )
        read_only_fields = (
            'id',
            'api_key',
        )

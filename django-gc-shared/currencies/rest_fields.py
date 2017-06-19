# -*- coding: utf-8 -*-

from rest_framework import serializers


class MoneyField(serializers.Field):
    def to_representation(self, obj):
        return {
            'amount': float(obj.amount) if hasattr(obj, 'amount') and obj.amount else '-.-',
            'currency': CurrencyField().to_representation(obj.currency) if hasattr(obj, 'currency') else '--',
            'display': unicode(obj)
        }

    def to_internal_value(self, data):
        raise NotImplementedError('...')


class CurrencyField(serializers.Field):
    def to_representation(self, obj):
        if obj:
            return {
                'slug': obj.slug,
                'symbol': obj.symbol,
                'name': obj.verbose_name,
                'is_metal': obj.is_metal
            }

    def to_internal_value(self, data):
        raise NotImplementedError('...')

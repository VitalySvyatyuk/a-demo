# -*- coding: utf-8 -*-
from rest_framework import serializers

from payments.models import DepositRequest, WithdrawRequest, BaseRequest
from currencies.rest_fields import MoneyField


class DepositRequestSerializer(serializers.ModelSerializer):
    account__mt4_id = serializers.ReadOnlyField(source='account.mt4_id')
    amount_money = MoneyField()
    status = serializers.ReadOnlyField()
    is_cancelable = serializers.ReadOnlyField(source="is_cancelable_by_user")
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = DepositRequest
        fields = (
            'id',
            'account',
            'account__mt4_id',
            'amount_money',
            'payment_system',
            #'params',

            'purse',

            'public_comment',
            'status',
            'status_display',
            'is_cancelable',

            'creation_ts',
        )
        read_only_fields = (
            'public_comment',

            'creation_ts',
        )


class WithdrawRequestSerializer(serializers.ModelSerializer):
    account__mt4_id = serializers.ReadOnlyField(source='account.mt4_id')
    amount_money = MoneyField()
    status = serializers.ReadOnlyField()
    is_cancelable = serializers.ReadOnlyField(source="is_cancelable_by_user")
    status_display = serializers.ReadOnlyField(source='get_status_display')

    class Meta:
        model = WithdrawRequest
        fields = (
            'id',
            'account',
            'account__mt4_id',
            'amount_money',
            'payment_system',
            #'params',

            'public_comment',
            'status',
            'status_display',
            'is_cancelable',

            'creation_ts',
        )
        read_only_fields = (
            'public_comment',

            'creation_ts',
        )


class BaseRequestSerializer(serializers.ModelSerializer):
    amount_money = MoneyField()
    is_cancelable = serializers.ReadOnlyField(source="is_cancelable_by_user")
    status = serializers.SerializerMethodField()
    account_id = serializers.SerializerMethodField()
    account__mt4_id = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    def get_account_id(self, obj):
        return obj.as_leaf_class().account.id

    def get_account__mt4_id(self, obj):
        return obj.as_leaf_class().account.mt4_id

    def get_status(self, obj):
        return obj.as_leaf_class().status

    def get_type(self, obj):
        return obj.as_leaf_class().__class__.__name__

    class Meta:
        model = BaseRequest
        fields = (
            'id',
            'account_id',
            'account__mt4_id',
            'amount_money',
            'payment_system',
            'type',
            'public_comment',
            'is_cancelable',
            'status',
            'creation_ts',
        )
        read_only_fields = (
            'public_comment',

            'creation_ts',
        )
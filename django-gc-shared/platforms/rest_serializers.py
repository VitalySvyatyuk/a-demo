# coding:utf-8
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from currencies.rest_fields import CurrencyField, MoneyField
from log.models import Event
from notification import models as notification
from platforms.forms import BINARY_OPTIONS_TYPE_CHOICES
from platforms.models import TradingAccount, AbstractTrade
from platforms.types import EUROPEAN_OPTIONS, get_account_type


class TradingAccountSerializer(serializers.ModelSerializer):
    currency = CurrencyField()
    display = serializers.ReadOnlyField(source='__unicode__')
    group = serializers.ReadOnlyField(source='group.slug')
    group_display = serializers.ReadOnlyField(source='group.__unicode__')
    platform_type = serializers.CharField()

    is_demo = serializers.BooleanField(read_only=True)
    is_options = serializers.BooleanField(read_only=True)
    no_inout = serializers.BooleanField(read_only=True)
    options_style = serializers.ReadOnlyField()
    is_contest = serializers.BooleanField(read_only=True)

    archived_status = serializers.ReadOnlyField()

    ib_data = serializers.SerializerMethodField()
    last_block_reason = serializers.SerializerMethodField()

    @staticmethod
    def get_last_block_reason(obj):
        if obj.last_block_reason:
            return obj.last_block_reason

    @staticmethod
    def get_ib_data(obj):
        if not obj.is_ib:
            return None
        from referral.models import Click
        return {
            'clicks': Click.objects.total(obj.mt4_id)
        }

    class Meta:
        model = TradingAccount
        fields = (
            'id',
            'display',
            'mt4_id',
            'currency',
            'group',
            'group_display',
            'platform_type',

            'is_demo',
            'is_options',
            'no_inout',
            'options_style',
            'is_contest',

            'ib_data',

            'creation_ts',
            'archived_status',
            'last_block_reason')
        read_only_fields = (
            'mt4_id',

            'creation_ts',
        )


# noinspection PyAbstractClass
class LeverageSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super(LeverageSerializer, self).__init__(*args, **kwargs)
        self.account = self.context['view'].get_object()
        self.fields["leverage"] = serializers.ChoiceField(
            label=_("The following leverage settings are available "
                    "for the current balance of your account:"),
            choices=[(leverage, '1:{}'.format(leverage)) for leverage in self.account.get_available_leverages()]
        )

    #fixes DRF bug #1932
    def validate_leverage(self, value):
        if int(value) == 0:
            raise serializers.ValidationError("500")
        if value == self.account.leverage:
            raise serializers.ValidationError(
                _("Leverage should be different from current one"))
        return value

    def apply_leverage(self):
        Event.LEVERAGE_CHANGED.log(self.account, {
            "from": self.account.leverage,
            "to": self.validated_data['leverage']
        })

        self.account.change_leverage(self.validated_data['leverage'])

        notification.send([self.account.user], "leverage_change", {
            "user_name": self.account.user.first_name,
            "account": self.account.mt4_id,
            "leverage": self.validated_data['leverage']
        })


# noinspection PyAbstractClass
class OptionsStyleSerializer(serializers.Serializer):
    style = serializers.ChoiceField(
        label=_("Binary options style"),
        choices=BINARY_OPTIONS_TYPE_CHOICES,
        help_text=_("American-style options can be closed "
                    "before expiration date, but have much lower "
                    "reward rate than European-style options"),
    )

    def __init__(self, *args, **kwargs):
        super(OptionsStyleSerializer, self).__init__(*args, **kwargs)
        self.account = self.context['view'].get_object()
        self.fields['style'].default = self.account.options_style or EUROPEAN_OPTIONS

    def apply_style(self):
        Event.OPTIONS_STYLE_CHANGED.log(self.account, {
            "from": self.account.options_style,
            "to": self.validated_data['style']
        })
        self.account.change_options_style(self.validated_data['style'])

    def validate(self, attrs):
        if self.account.open_orders_count():
            raise serializers.ValidationError(
                _("You need to close all trades before changing options style"))
        return attrs


# noinspection PyAbstractClass
class TradeSerializer(serializers.Serializer):
    ticket = serializers.IntegerField()
    open_time = serializers.DateTimeField()
    symbol = serializers.CharField()
    volume = serializers.IntegerField()
    open_price = serializers.FloatField()
    sl = serializers.FloatField()
    tp = serializers.FloatField()
    close_price = serializers.FloatField()
    commission = serializers.FloatField()
    swaps = serializers.FloatField()
    comment = serializers.CharField()

    cmd_name = serializers.CharField(source='get_cmd_display')
    profit = serializers.DecimalField(max_digits=100, decimal_places=2)
    close_time = serializers.SerializerMethodField()

    # Special case for MT4 close time, where None=01-01-1970
    @staticmethod
    def get_close_time(obj):
        if obj.close_time.year == 1970:
            return None
        else:
            return obj.close_time


# noinspection PyAbstractClass
class TradingAccountAgentSerializer(serializers.Serializer):
    mt4_id = serializers.ReadOnlyField(source="login")
    balance = MoneyField(source="balance_money")
    regdate = serializers.DateTimeField()
    country = serializers.ReadOnlyField()
    city = serializers.ReadOnlyField()
    phone_mobile = serializers.ReadOnlyField(source="mt4account.user.profile.phone_mobile")
    email = serializers.ReadOnlyField(source="mt4account.user.email")

    @staticmethod
    def get_group_display(obj):
        group = unicode(get_account_type(obj.group))
        return group
    group_display = serializers.SerializerMethodField()

    @staticmethod
    def get_name(obj):
        if not obj.accounts:
            return obj.name
        return obj.accounts[0].user.profile.get_full_name()
    name = serializers.SerializerMethodField()


# noinspection PyAbstractClass
class DemoDepositSerializer(serializers.Serializer):
    value = serializers.DecimalField(
        label=_("Amount"),
        max_digits=9,
        decimal_places=2
    )

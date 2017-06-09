# coding=utf-8
from datetime import datetime, timedelta

from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

from friend_recommend.models import Recommendation
from platforms.models import TradingAccount


class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ('name', 'email')

    def __init__(self, *args, **kwargs):
        super(RecommendationSerializer, self).__init__(*args, **kwargs)
        self.user = self.context["request"].user
        ib_accounts = self.user.accounts.real_ib()
        if ib_accounts:
            self.fields["ib_account"] = serializers.ChoiceField(
               label=_("Account"),
               help_text=_("Select one of your accounts."),
               choices=((acc.mt4_id, unicode(acc)) for acc in ib_accounts),
               required=True,
            )

    def validate_ib_account(self, value):
        account_number = value
        if account_number:
            ib_account = TradingAccount.objects.filter(user=self.user, mt4_id=account_number).first()
            if ib_account and ib_account in self.user.accounts.real_ib():
                value = ib_account
            else:
                raise serializers.ValidationError("Invalid account number")
        return value

    def validate(self, attrs):
        errors = {}

        email = attrs.get('email')
        user = self.user
        if user and email:
            if Recommendation.objects.filter(user=user,
                                             email=email,
                                             creation_ts__gte=datetime.now() - timedelta(90)).exists():
                errors['email'] = u'Вы уже посылали приглашение на этот email'
            if user.email.lower() == email:
                errors['email'] = u'Вы не можете посылать приглашение самому себе'
            if Recommendation.objects.filter(user=user, creation_ts__gte=datetime.now() - timedelta(1)).count() >= 20:
                errors['email'] = u'Вы не можете приглашать более 20 человек в день'

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

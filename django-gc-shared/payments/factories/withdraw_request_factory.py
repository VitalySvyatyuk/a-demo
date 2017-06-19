# -*- coding: utf-8 -*-
import factory
from faker import Factory
from payments.models import WithdrawRequest
from platforms.factories.account_factories import TradingAccountFactory
from django.db.models.signals import pre_save, post_save

fake = Factory.create()
fake_ru = Factory.create('ru_RU')


class WithdrawRequestFactory(factory.DjangoModelFactory):
    class Meta:
        model = WithdrawRequest

    account = factory.SubFactory(TradingAccountFactory)
    amount = 100
    currency = 'USD'
    payment_system = 'webmoney'
    active_balance = 1000


@factory.django.mute_signals(pre_save, post_save)
class WithdrawRequestFactorySignalLess(WithdrawRequestFactory):
    pass

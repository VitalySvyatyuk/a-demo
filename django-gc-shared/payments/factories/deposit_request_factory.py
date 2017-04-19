# -*- coding: utf-8 -*-
import factory
from faker import Factory
from payments.models import DepositRequest
from platforms.factories.account_factories import TradingAccountFactory
from django.db.models.signals import pre_save, post_save
from payments.utils import load_payment_system

fake = Factory.create()


class DepositRequestFactory(factory.DjangoModelFactory):
    class Meta:
        model = DepositRequest

    account = factory.SubFactory(TradingAccountFactory)
    amount = 100
    currency = 'USD'
    payment_system = load_payment_system("yandex")
    active_balance = 1000
    purse = factory.LazyAttribute(lambda o: fake.credit_card_number())
    params = {}


@factory.django.mute_signals(pre_save, post_save)
class DepositRequestFactorySignalLess(DepositRequestFactory):
    pass

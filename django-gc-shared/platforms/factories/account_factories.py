# -*- coding: utf-8 -*-
import factory
from faker import Factory
from platforms.models import TradingAccount
from profiles.factories.user_factory import UserFactory
import random

fake = Factory.create()
fake_ru = Factory.create('ru_RU')
demo_mt4accounts = 1023400, 1096231, 1098168, 1130023, 1144455


class TradingAccountFactory(factory.DjangoModelFactory):
    class Meta:
        model = TradingAccount

    user = factory.SubFactory(UserFactory)
    mt4_id = factory.LazyAttribute(lambda o: random.choice(demo_mt4accounts))
    last_block_reason = None  # type: None

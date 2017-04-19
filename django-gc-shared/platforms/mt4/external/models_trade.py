# -*- coding: utf-8 -*-
from django.db import models
from platforms.models import TradeQuerySet, AbstractTrade


class RealTrade(AbstractTrade):
    objects = TradeQuerySet.as_manager()
    # This is the only way it can be done with Django model inheritance
    login = models.ForeignKey('RealUser', db_column='LOGIN')

    class Meta:
        db_table = u'mt4_trades'
        app_label = 'external'


class DemoTrade(AbstractTrade):
    objects = TradeQuerySet.as_manager()
    login = models.ForeignKey('DemoUser', db_column='LOGIN', related_name="mt4trade")

    class Meta:
        db_table = u'mt4_trades'
        app_label = 'external'


class ArchiveTrade(AbstractTrade):
    objects = TradeQuerySet.as_manager()
    login = models.ForeignKey('ArchiveUser', db_column='LOGIN', related_name="mt4trade")

    class Meta:
        db_table = u'mt4_trades'
        app_label = 'external'


trade = {
    "db_archive": ArchiveTrade,
    "demo": DemoTrade,
    "real": RealTrade,
    "default": RealTrade,
}

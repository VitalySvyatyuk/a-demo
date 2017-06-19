# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from platforms.models import AbstractQuote
from platforms.types import INSTANT_EXECUTION, MARKET_EXECUTION


class Mt4Instruments(models.Model):
    """
    Available financial instruments.
    """
    symbol = models.CharField(verbose_name=_("Symbol"),
                              max_length=16, db_column="Symbol", primary_key=True)
    # tick represents the smallest possible price change on the right side of a decimal point
    tic_size = models.CharField(verbose_name=_("Tick size"),
                                max_length=16, db_column="TIC_size", null=True)
    # ?
    open_price = models.FloatField(verbose_name=_("Open price"),
                                   db_column="OPEN_PRICE", null=True)
    # margin level to stop out
    stops_level = models.IntegerField(verbose_name=_("Stop out level"),
                                      null=True, db_column="Stops_Level")
    # cost of long swap
    swap_long = models.CharField(verbose_name=_("Swap long"),
                                 max_length=100, db_column="Swap_Long", null=True)
    # cost of short swap
    swap_short = models.CharField(verbose_name=_("Swap short"),
                                  max_length=100, db_column="Swap_Short", null=True)
    # ?
    contr_size = models.FloatField(verbose_name=_("Contract size"),
                                   db_column="Contr_Size", null=True)
    # ?
    tic_cost = models.CharField(verbose_name=_("Tick cost"),
                                max_length=100, db_column="Tic_cost", null=True)
    # margin size
    margin = models.CharField(verbose_name=_("Margin"),
                              max_length=32, db_column="Margin", null=True)
    # initial margin
    margin_initial = models.CharField(verbose_name=_("Initial margin"),
                                      max_length=32, db_column="Margin_initial", null=True)
    # currency of instrument
    currency = models.CharField(verbose_name=_("Currency"),
                                max_length=16, db_column="Cur", null=True)
    # instrument group
    group = models.CharField(verbose_name=_("Group"),
                             max_length=32, db_column="Group")
    # minimal spread on instrument
    min_spread = models.CharField(verbose_name=_("Min. spread"),
                                  max_length=8, db_column="min. Spread")
    # maximal spread on instrument
    max_spread = models.CharField(verbose_name=_("Max. spread"),
                                  max_length=8, db_column="max. Spread")
    # average spread on instrument
    avg_spread = models.CharField(verbose_name=_("Avg. spread"),
                                  max_length=8, db_column="avg. Spread")
    # ?
    spread = models.CharField(verbose_name=_("Spread"),
                              max_length=8, db_column="Spread", default="0")
    # currency of margin
    margin_cur = models.CharField(verbose_name=_("Margin currency"),
                                  max_length=16, db_column="margin_Cur", null=True)
    # title of instrument
    title = models.CharField(verbose_name=_("Title"),
                             max_length=255, db_column="Title", null=True)
    # ?
    night_margin = models.CharField(verbose_name=_("Night margin"),
                                    max_length=32, db_column="Night_Margin", null=True)
    # commission
    commission = models.CharField(verbose_name=_("Commission"),
                                  max_length=32, db_column="Comission", default='20.00 USD')
    # default volume ?
    volume = models.IntegerField(verbose_name=_("Volume"),
                                 db_column="Volume", null=True)

    class Meta:
        db_table = "instruments"
        app_label = 'external'


class Mt4Quote(AbstractQuote):
    class Meta:
        db_table = "mt4_prices"
        app_label = 'external'


class Mt4OpenPrice(models.Model):
    EXECUTION_TYPES = (
        (1, INSTANT_EXECUTION),
        (2, MARKET_EXECUTION),
    )

    TRADING_STATUSES = (
        (2, "Trading allowed"),
        (1, "No new positions allowed"),
        (0, "Trading is closed"),
    )

    symbol = models.CharField(verbose_name=_("Symbol"),
                              max_length=16, db_column="Symbol", primary_key=True)
    open_price = models.FloatField(verbose_name=_("Open price"),
                                   db_column="OPEN_PRICE", null=True)
    spread_digits = models.IntegerField(verbose_name=_("Spread digits"),
                                        db_column="digits", null=True)
    execution_type = models.IntegerField(verbose_name=_("Execution type"), db_column="exemode", null=True,
                                         choices=EXECUTION_TYPES)
    trade_status = models.IntegerField(verbose_name=_("Is trading allowed?"), db_column="trade", null=True,
                                       choices=TRADING_STATUSES)

    class Meta:
        db_table = "OPEN_PRICE"
        app_label = 'external'

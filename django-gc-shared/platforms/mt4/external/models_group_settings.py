# -*- coding: utf-8 -*-
from django.db import models


class AbstractGroupSettings(models.Model):
    """
    Account groups settings.
    """
    # name of group
    group = models.CharField(max_length=16, db_column="ACC_GROUPNAME", primary_key=True)
    # type of instruments (forex/futures/options)
    sec_group = models.CharField(max_length=16, db_column="SEC_GROUPNAME")
    # determines if instruments are visible to group
    show = models.BooleanField(db_column="SHOW")
    # determines if instruments are tradable by group
    trade = models.BooleanField(db_column="TRADE")
    # who is to execute order? automatical/manual by dealer
    execution = models.CharField(max_length=64, db_column="EXECUTION")
    # commission settings
    # base commission
    commission_base = models.FloatField(db_column="COMM_BASE")
    # type of commission taken
    commission_type = models.CharField(max_length=45, db_column="COMM_TYPE")
    # is commission per lot or trade
    commission_lots = models.CharField(max_length=45, db_column="COMM_LOTS")
    # agent commission - not used
    commission_agent = models.FloatField(db_column="COMM_AGENT")
    commission_agent_type = models.CharField(max_length=45, db_column="COMM_AGENT_TYPE")
    commission_agent_lots = models.PositiveIntegerField(db_column="COMM_AGENT_LOTS")
    # spread balance (>0 up shift, <0 down shift)
    spread_diff = models.PositiveIntegerField(db_column="SPREAD_DIFF")
    # min lot size
    lot_min = models.PositiveIntegerField(db_column="LOT_MIN")
    # max lot size
    lot_max = models.PositiveIntegerField(db_column="LOT_MAX")
    # lot change step
    lot_step = models.PositiveIntegerField(db_column="LOT_STEP")
    # instant execution max deviation to issue requote
    ie_deviation = models.PositiveIntegerField(db_column="IE_DEVIATION")
    # orders "on request" - not used
    confirmation = models.PositiveIntegerField(db_column="CONFIRMATION")
    # closing by counter order - not used
    trade_rights = models.CharField(max_length=64, db_column="TRADE_RIGHTS")
    # flag connected with ie_deviation
    ie_quick_mode = models.BooleanField(db_column="IE_QUICK_MODE")
    # type of positions transfer to the next day
    autocloseout_mode = models.CharField(max_length=64, db_column="AUTOCLOSEOUT_MODE")
    # client taxation
    commission_tax = models.FloatField(db_column="COMM_TAX")


    class Meta:
        abstract = True


class Mt4RealGroupSettings(AbstractGroupSettings):
    class Meta:
        db_table = "jb_secgroup_settings"
        app_label = 'external'


class Mt4DemoGroupSettings(AbstractGroupSettings):
    class Meta:
        db_table = "mt4_secgroup_settings"
        app_label = 'external'


mt4_group_settings = {
    "demo": Mt4RealGroupSettings,
    "real": Mt4RealGroupSettings,
    "default": Mt4RealGroupSettings,
    "gtmarkets": Mt4RealGroupSettings,
}

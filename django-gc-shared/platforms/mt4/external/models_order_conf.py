# -*- coding: utf-8 -*-
from django.db import models
from datetime import datetime


class BaseOrderConf(models.Model):
    """
    Orders configurations. Used in webtrader for order examination.
    """
    # ticker
    symbol = models.CharField(max_length=12, db_column='SYMBOL')
    # Really, acc_groupname is not primary key. Just webtrader_confs it's mysql view and have not PK field
    acc_groupname = models.CharField(max_length=16, db_column='ACC_GROUPNAME', primary_key=True)
    # min allowable order volume value
    lot_min = models.PositiveIntegerField(db_column='LOT_MIN')
    # max allowable order volume value
    lot_max = models.PositiveIntegerField(db_column='LOT_MAX')
    # order volume value must be multiplicity of lost_step
    lot_step = models.PositiveIntegerField(db_column='LOT_STEP')
    # max numbers after ',' in T/L, S/L, and price values
    digits = models.PositiveIntegerField(db_column='DIGITS')
    # at which weekday are these settings active
    weekday = models.CharField(max_length=12, db_column='WEEKDAY')
    # if 2 trading is allowed, if 1 only closing
    trade = models.PositiveIntegerField(db_column='TRADE')

    # time in minutes from the start of the day
    open_session_1 = models.PositiveIntegerField(db_column='OPEN_SESSION_1_TRADE')
    close_session_1 = models.PositiveIntegerField(db_column='CLOSE_SESSION_1_TRADE')
    open_session_2 = models.PositiveIntegerField(db_column='OPEN_SESSION_2_TRADE')
    close_session_2 = models.PositiveIntegerField(db_column='CLOSE_SESSION_2_TRADE')
    open_session_3 = models.PositiveIntegerField(db_column='OPEN_SESSION_3_TRADE')
    close_session_3 = models.PositiveIntegerField(db_column='CLOSE_SESSION_3_TRADE')

    class Meta:
        abstract = True

    def is_session_open(self):
        """
        Determine if trading session currently available.
        """
        count_minutes = datetime.now().time().hour * 60 + datetime.now().time().minute

        for session in [1, 2, 3]:
            session_start = getattr(self, "open_session_%d" % session)
            session_end = getattr(self, "close_session_%d" % session)
            if session_end == 0:
                session_end = 60 * 24

            if session_start < count_minutes < session_end:
                return True
        return False


class RealOrderConf(BaseOrderConf):
    class Meta:
        db_table = "jb_webtrader_confs"  # `gcmtsrv_real` database (see more in webtrader.routers)
        app_label = 'external'


class DemoOrderConf(BaseOrderConf):
    class Meta:
        db_table = "jb_webtrader_confs"  # `gcmtsrv_demo` database (see more in webtrader.routers)
        app_label = 'external'


mt4_order_config = {
    "demo": RealOrderConf,
    "real": RealOrderConf,
    "default": RealOrderConf,
}
from django.db import models


class AbstractSymbolConfig(models.Model):
    # ticker
    symbol = models.CharField(max_length=12, primary_key=True)
    # index of function to calculate profits (they differs with rounding algorithms)
    profit_mode = models.PositiveIntegerField()
    # cost of minimal tick in units
    tick_price = models.FloatField(db_column="TICK_VALUE")
    # minimal tick unit
    tick_size = models.FloatField()
    # ticker currency
    currency = models.CharField(max_length=12, db_column="CURRENCY")
    # instrument group
    group = models.CharField(max_length=16, db_column="GTYPE")

    # margin calculation settings mode
    margin_mode = models.PositiveIntegerField()
    # initial margin (used by default)
    margin_initial = models.FloatField(db_column="MARGIN_INITAL")
    # margin currency
    margin_currency = models.CharField(max_length=12)
    # percent of charged commission
    margin_divider = models.FloatField()
    # default contract size
    contract_size = models.FloatField()

    # words about
    description = models.CharField(max_length=64)

    # source of quotes
    source = models.CharField(max_length=12)
    # number of digits after comma
    digits = models.PositiveIntegerField()
    # can trade?
    trade = models.PositiveIntegerField()
    # background color in terminal
    background_color = models.IntegerField()
    # position in terminal
    count = models.PositiveIntegerField()
    # absolute position in terminal
    count_original = models.PositiveIntegerField()
    # allow quotes in realtime
    realtime = models.PositiveIntegerField()
    # skip first n quotes at the beginning
    starting = models.PositiveIntegerField()
    # time when ticker will stop trading - not used
    expiration = models.PositiveIntegerField()
    # reserved field?
    profit_reserved = models.PositiveIntegerField(db_column="PROFIT_REZERVED")
    # quotes filtration settings
    filter = models.PositiveIntegerField()
    filter_counter = models.PositiveIntegerField()
    filter_limit = models.PositiveIntegerField()
    filter_reserved = models.PositiveIntegerField()
    # log past ticks
    logging = models.PositiveIntegerField()
    # spread size
    spread = models.PositiveIntegerField()
    # spread balance (>0 if up shifted, <0 else)
    spread_balance = models.PositiveIntegerField()
    # type of execution of this ticker
    exemode = models.PositiveIntegerField()
    # is swap enabled
    swap_enable = models.PositiveIntegerField()
    # type of swap
    swap_type = models.PositiveIntegerField()
    # swap for long positions
    swap_long = models.FloatField()
    # swap for short positions
    swap_short = models.FloatField()
    # swap rollover
    swap_rollover_3_days = models.PositiveIntegerField(db_column="SWAP_ROLLOVER3DAYS")
    # stop level
    stops_level = models.PositiveIntegerField()
    # type of pending order processing
    gtc_pendings = models.PositiveIntegerField()
    # maintained margin
    margin_maintenance = models.FloatField()
    # volume of hedged margin (in case of hedged operations)
    margin_hedged = models.FloatField()
    # actually number of digits after comma
    point = models.FloatField()
    # percent of charged margin
    multiply = models.FloatField()
    # not used
    bid_tick_value = models.FloatField(db_column="BID_TICKVALUE")
    # not used
    ask_tick_value = models.FloatField(db_column="ASK_TICKVALUE")
    # long positions only
    long_only = models.PositiveIntegerField()
    # size of maximal allowed order lot in intant mode, bigger lots will be executed in by-request mode
    instant_max_volume = models.PositiveIntegerField()
    # when client order price is near current market price order/position modification is forbidden
    # when current market price is near SL/TP their modifications are forbidden
    freeze_level = models.PositiveIntegerField()
    # last modification time
    modify_time = models.DateTimeField()

    class Meta:
        abstract = True


class SymbolConfig(AbstractSymbolConfig):
    class Meta:
        db_table = "mt4_symbolconfig"
        app_label = 'external'


class DemoSymbolConfig(AbstractSymbolConfig):
    class Meta:
        db_table = "mt4_symbolconfig"
        app_label = 'external'


symbol_config = {
    "demo": DemoSymbolConfig,
    "real": SymbolConfig,
    "default": SymbolConfig,
}

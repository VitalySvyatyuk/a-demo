# -*- coding: utf-8 -*-

from django.db import models, connections
from django.http import Http404

from platforms.mt4.external.models_other import Mt4Instruments
from shared.models import CustomManagerMixin

from django.utils.translation import ugettext_lazy as _
from currencies import currencies

CURRENCY_CHOICES = currencies.choices()


class InvalidInstrumentError(Http404):
    """
    Invalid instrument exception
    """


DESC_OBJECT_TYPES = (
    ('instrument', "Instrument"),
    ('symbol', "Symbol"),
)


class SymbolDescription(models.Model):
    symbol = models.CharField("Symbol", max_length=25, null=False)
    type = models.CharField("Object Type", max_length=100, null=False, choices=DESC_OBJECT_TYPES, default='symbol')
    description = models.TextField("Description", null=True, blank=True)

    class Meta:
        verbose_name = 'Symbol description'

    def __unicode__(self):
        return self.description


class SpecsGroupQuerySet(models.query.QuerySet):

    def eu(self):
        return self.filter()

    def us(self):
        return self.filter(account_group__endswith="_us")


class SpecsGroupManager(models.Manager, CustomManagerMixin):

    def get_queryset(self):
        return SpecsGroupQuerySet(self.model)


class InstrumentsByGroup(models.Model):

    account_group = models.CharField(max_length=32, db_column="MT_GROUP", null=False)
    symbol_group = models.CharField(max_length=32, db_column="SYMBOL_GROUP", null=False, primary_key=True)
    changed_at = models.DateTimeField(db_column="MODIFY_TIME")

    class Meta:
        db_table = "mt4_securities"

    objects = SpecsGroupManager()

    def __unicode__(self):
        return u"%s %s" % (self.account_group, self.symbol_group)


class SymbolsByInstrument(models.Model):
    symbol = models.CharField(max_length=100, db_column="symbol_name", null=False, primary_key=True)
    instrument = models.CharField(max_length=100, db_column="instrument_name", null=True)
    update_ts = models.DateTimeField(auto_now=True, db_column="MODIFY_TIME")

    class Meta:
        db_table = "mt4_instruments"

    def __unicode__(self):
        return u"{} ({})".format(self.symbol, self.instrument)


class Instruments(Mt4Instruments):

    class Meta:
        proxy = True


class InstrumentSpecificationCategory(models.Model):
    name = models.CharField(_("Name"), max_length=150)
    slug = models.SlugField(_("Slug"), help_text=_('short url name'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("Instrument specification category")
        verbose_name_plural = _("Instrument specification categories")


class InstrumentSpecification(models.Model):
    instrument = models.CharField(_("Instrument"), max_length=100)
    description = models.TextField(_('Description'))
    currency = models.CharField(_("Currency"), max_length=100)
    min_price_change = models.CharField(_("Minimum price change"), max_length=100)
    min_order_size = models.CharField(_("Minimum contract size"), max_length=100)
    min_order_size_change = models.CharField(_("Minimum contract size change"), max_length=100)
    min_order_pip_value = models.CharField(_("Pip value per minimum contract"), max_length=100)
    swap_long = models.CharField(_("SWAP Long"), max_length=100)
    swap_short = models.CharField(_("SWAP Short"), max_length=100)
    weekday_margin = models.CharField(_("Weekday pledge"), max_length=100)
    weekend_margin = models.CharField(_("Weekend pledge"), max_length=100)
    category = models.ForeignKey(InstrumentSpecificationCategory, verbose_name=_("Category"))

    def __unicode__(self):
        return self.instrument

    class Meta:
        verbose_name = _("Instrument specification")
        verbose_name_plural = _("Instrument specification")


class Calculator(object):

    @classmethod
    def get_data(cls):

        INSTRUMENT_GROUPS = {
            "Forex": ["FOREX MAJORS", "FOREX EXT 1", "FOREX EXT 2", "FOREX METALS"],
            "CFD Stock": ["CFD STOCK USA", "Russian STOCK"],
            "CFD Metals": ["CFD METALS"],
            "CFD Grains": ["CFD GRAINS"],
            "CFD Energies": ["CFD ENERGIES"],
            "CFD Forex": ["CFD CURRENCIES"],
            "CFD Indices": ["CFD INDICES"],
            "CFD Softs": ["CFD SOFTS"],
            "CFD Meats": ["CFD MEATS"],
            "ECN Forex": ["ECN FOREX"],
            # "Fx+ Forex": ["FX+"],
            "Options": ["OPTIONS"],
        }
        account_types_data = {
            "ECN.MT": {
                "currencies": ["USD", "EUR", "RUR", "GBP", "JPY", "CHF", "GOLD", "SILVER"],
                "leverages": ["1:1", "1:10", "1:50", "1:100", "1:200", "1:500", "1:2000"],
                "default_leverage": "1:100",
                "groups": {"Forex": {}}
            },
            "ECN.PRO": {
                "currencies": ["USD", "EUR", "RUR", "GBP", "JPY", "CHF", "GOLD", "SILVER"],
                "leverages": ["1:1", "1:10", "1:50", "1:100", "1:200", "1:500", "1:2000"],
                "default_leverage": "1:100",
                "groups": {"Forex": {}, "CFD Stock": {}, "CFD Metals": {}, "CFD Grains": {},
                           "CFD Forex": {}, "CFD Indices": {}, "CFD Energies": {}, "CFD Softs": {},
                           "CFD Meats": {}, }
            },
            "ECN.INVEST": {
                "currencies": ["USD"],
                "leverages": ["1:1", "1:10", "1:50", "1:100"],
                "default_leverage": "1:100",
                "groups": {"ECN Forex": {}}
            },
            # "SwapFree": {
            #     "currencies": ["USD"],
            #     "leverages": ["1:1", "1:10", "1:50", "1:100", "1:200", "1:500", "1:2000"],
            #     "default_leverage": "1:100",
            #     "groups": {"Forex": {}, "CFD Stock": {}, "CFD Metals": {}, "CFD Grains": {},
            #                "CFD Forex": {}, "CFD Indices": {}, "CFD Energies": {}, "CFD Softs": {},
            #                "CFD Meats": {}, }
            # },
            # "FX+": {
            #     "currencies": ["RUR"],
            #     "leverages": ["1:1", "1:10", "1:50", "1:100"],
            #     "default_leverage": "1:100",
            #     "groups": {"Fx+ Forex": {}}
            # }
        }
        db_result = {}
        sql = (
            "SELECT "
            "spec.Symbol, spec.GTYPE, pric.BID, pric.ASK, spec.CONTRACT_SIZE, spec.TICK_SIZE, "
            "spec.TICK_VALUE, spec.MARGIN_INITAL, spec.CURRENCY, spec.MARGIN_CURRENCY, "
            "spec.PROFIT_MODE, spec.MARGIN_MODE, spec.MARGIN_DIVIDER, spec.DIGITS "
            "FROM "
            "`gcmtsrv_real`.`mt4_symbolconfig` spec JOIN `gcmtsrv_real`.`mt4_prices` pric "
            "ON "
            "spec.Symbol = pric.SYMBOL "
        )
        engine = connections['specifications'].cursor()
        engine.execute(sql)
        instruments = engine.fetchall()
        exchange_rates = {}

        if instruments:
            for instrument in instruments:
                if instrument[0] == "USDRUR":
                    exchange_rates["USDRUR_ask"] = instrument[3]  # ruble exchange rate
                elif instrument[0] == "USDXAU":
                    exchange_rates["USDXAU_ask"] = instrument[3]  # GOLD exchange rate
                elif instrument[0] == "USDXAG":
                    exchange_rates["USDXAG_ask"] = instrument[3]  # SILVER exchange rate

                if db_result.get(instrument[1], None):
                    db_result[instrument[1]].update({instrument[0]: {"bid": instrument[2], "ask": instrument[3],
                                                                     "contr_size": instrument[4],
                                                                     "tick_size": 1.0/10**instrument[13] if instrument[10] == 0 or instrument[10] == 1 else instrument[5],  # if profit_mode == 0 or 1 then tick_size = 1.0/10**DIGITS
                                                                     "tick_price": instrument[6],
                                                                     "margin_internal": instrument[7],
                                                                     "currency": instrument[8],
                                                                     "margin_currency": instrument[9],
                                                                     "profit_mode": instrument[10],
                                                                     "margin_mode": instrument[11],
                                                                     "percentage": 100.0 / instrument[12],
                                                                     }})

                else:
                    db_result[instrument[1]] = {instrument[0]: {"bid": instrument[2], "ask": instrument[3],
                                                                "contr_size": instrument[4],
                                                                "tick_size": 1.0/10**instrument[13] if instrument[10] == 0 or instrument[10] == 1 else instrument[5],  # if profit_mode == 0 or 1 then tick_size = 1.0/10**DIGITS
                                                                "tick_price": instrument[6],
                                                                "margin_internal": instrument[7],
                                                                "currency": instrument[8],
                                                                "margin_currency": instrument[9],
                                                                "profit_mode": instrument[10],
                                                                "margin_mode": instrument[11],
                                                                "percentage": 100.0 / instrument[12],
                                                                }}
            for group_name in INSTRUMENT_GROUPS:
                group_data = {}
                for item in INSTRUMENT_GROUPS[group_name]:
                    group_data.update(db_result[item])
                INSTRUMENT_GROUPS[group_name] = group_data
            for acc_type in account_types_data:
                for sym_group in account_types_data[acc_type]["groups"]:
                    account_types_data[acc_type]["groups"][sym_group] = INSTRUMENT_GROUPS[sym_group]
        return account_types_data, exchange_rates

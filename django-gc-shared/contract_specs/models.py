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
        import re
        from collections import OrderedDict
        data = OrderedDict()
        from platforms.mt4.external.models import Mt4Quote
        mt4quotes = Mt4Quote.objects.order_by('symbol').all()
        for q in mt4quotes:
            if re.match(r"^[\dA-Z]+$", q.symbol):
                data[q.symbol] = {'bid': q.bid, 'ask': q.ask, 'spread': q.spread, 'digits': q.digits}
        return data


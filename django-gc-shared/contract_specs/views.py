# -*- coding: utf-8 -*-

import json
from collections import defaultdict
from datetime import datetime

from annoying.decorators import render_to
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
from django.utils.translation import get_language
from django.shortcuts import get_object_or_404, redirect

from contract_specs.models import (
    InstrumentsByGroup, Instruments, Calculator,
    InstrumentSpecificationCategory, InstrumentSpecification)
from platforms.types import StandardAccountType, get_account_type

COLUMNS = {
    "forex_majors": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                     "contr_size", "min_spread", "max_spread", "avg_spread"],
    "forex_majors_ie": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                        "contr_size", "spread"],
    "forex_ext_1": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                    "contr_size", "min_spread", "max_spread", "avg_spread"],
    "forex_ext_1_ie": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                       "contr_size", "spread"],
    "forex_ext_2": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                    "contr_size", "min_spread", "max_spread", "avg_spread"],
    "forex_ext_2_ie": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                       "contr_size", "spread"],
    "forex_metals": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                     "contr_size", "min_spread", "max_spread", "avg_spread"],
    "forex_metals_ie": ["symbol", "tic_size", "contr_size", "stops_level", "swap_long",
                        "swap_short", "min_spread", "max_spread", "avg_spread", "margin", "currency"],
    "cfd_metals": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                   "currency", "min_spread", "max_spread", "avg_spread", "night_margin", "commission"],
    "cfd_currencies": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                       "currency", "night_margin", "commission"],
    "cfd_energies": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                     "currency", "night_margin", "commission"],
    "cfd_grains": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                   "currency", "night_margin", "commission"],
    "cfd_indices": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                    "currency", "night_margin", "commission"],
    "cfd_softs": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                  "currency", "night_margin", "commission"],
    "cfd_meats": ["symbol", "title", "tic_size", "tic_cost", "margin", "margin_initial",
                  "currency", "night_margin", "commission"],
    "cfd_stock_usa": ["symbol", "tic_size", "contr_size", "stops_level", "swap_long",
                      "swap_short", "margin", "currency", "commission"],
    "russian_stock": ["symbol", "tic_size", "contr_size", "stops_level", "swap_long",
                      "swap_short", "margin", "currency", "commission"],
    "ecn_forex": ["symbol", "title", "tic_size", "stops_level", "swap_long", "swap_short",
                  "contr_size", "min_spread", "max_spread", "avg_spread", "commission"],
#    "fx+": ["symbol", "tic_size", "stops_level", "swap_long", "swap_short",
#            "contr_size", "min_spread", "max_spread", "avg_spread"],
    "options": ["symbol", "period", "start", "min_time", "max_time", "win_5", "win_5_15",
                "win_15_30", "win_30", "loss", "nil", "bonus"],
    "options_us": ["symbol", "period", "start", "min_time", "max_time", "win", "loss",
                   "nil", "close_win", "close_percent"],
    "free_swap": ["symbol", "tic_size", "stops_level", "contr_size",
                  "min_spread", "max_spread", "avg_spread"],
    "cryptocurrency": ["symbol", "title", "tic_size", "swap_long", "swap_short", "margin", "commission"]
}

INSTRUMENTS_MAP = {
    "CFD CURRENCIES": "CFD",
    "CFD ENERGIES": "CFD",
    "CFD GRAINS": "CFD",
    "CFD INDICES": "CFD",
    "CFD MEATS": "CFD",
    "CFD METALS": "CFD",
    "CFD SOFTS": "CFD",
    "CFD STOCK USA": "STOCKS",
    "Russian STOCK": "STOCKS",
    "FOREX EXT 1": "FOREX",
    "FOREX EXT 2": "FOREX",
    "FOREX MAJORS": "FOREX",
    "FOREX METALS": "FOREX",
    "FOREX EXT 1 IE": "FOREX",
    "FOREX EXT 2 IE": "FOREX",
    "FOREX MAJORS IE": "FOREX",
    "FOREX METALS IE": "FOREX",
    "ECN FOREX": "FOREX",
#    "FX+": "FOREX",
    "FREE_SWAP": "FOREX",
    "CryptoCurrency": "FOREX"
}


def mutate_name(name):
    return name.lower().replace(" ", "_")


@render_to("marketing_site/index.html")
def symbols_for_instrument(request, acc_type_raw="realstandard", spec_type_raw=""):
    cache_key = "contract_specs_all_instruments_%s" % get_language()
    res = cache.get(cache_key)

    if res:
        res = json.loads(res)
    else:
        res = {}

        for acc_type in [StandardAccountType]:

            # qs = InstrumentsByGroup.objects.filter(account_group__iregex=acc_type.regex.pattern)
            # FIXME: When going to production
            qs = InstrumentsByGroup.objects.filter(account_group__iregex=r'^realstd_.*$')

            res[acc_type.slug] = defaultdict(dict)
            for group_raw in (
                    qs.filter(symbol_group__in=INSTRUMENTS_MAP.keys())
                      .values_list("symbol_group", flat=True)
                      .order_by("symbol_group").distinct()):

                group = mutate_name(group_raw)
                try:
                    tab_name = INSTRUMENTS_MAP[group_raw]
                except KeyError:
                    continue
                values_list = COLUMNS[group]

                res[acc_type.slug][tab_name][group_raw] = {
                    "data": list(Instruments.objects.filter(group=group_raw)
                                                    .order_by("group")
                                                    .values_list(*values_list)),
                    "columns": [unicode(Instruments._meta.get_field_by_name(f_name)[0].verbose_name)
                                for f_name in values_list]
                }

            res[acc_type.slug].default_factory = None

        # cache until 5 AM
        if datetime.now().hour < 5:
            # cache gonna to expire today!
            timeout = int(((datetime.now() + relativedelta(hour=5, minute=0, second=0))-datetime.now()).total_seconds())
        else:
            # cache is gonna to expire tomorrow
            timeout = int(((datetime.now() + relativedelta(days=1, hour=5, minute=0, second=0))-datetime.now()).total_seconds())
        cache.set(cache_key, json.dumps(res), timeout)

    return {
        "acc_data": res['realstandard'],
        "acc_type": get_account_type(acc_type_raw) or StandardAccountType,
        "spec_type": (spec_type_raw or '').upper()
    }


def instrument_specification(request, slug=None):
    if slug:
        category = get_object_or_404(
            InstrumentSpecificationCategory, slug=slug)
    else:
        category = InstrumentSpecificationCategory.objects.first()
    instruments = InstrumentSpecification.objects.filter(category=category)
    search_text = request.GET.get("search")
    if search_text:
        instruments = instruments.filter(instrument__icontains=search_text)
    return {
        "category": category,
        "instruments": instruments,
        "categories": InstrumentSpecificationCategory.objects.all()
    }


specifications = render_to(
    "marketing_site/pages/specification.jade")(instrument_specification)
margin_requirements = render_to(
    "marketing_site/pages/margin.jade")(instrument_specification)


@render_to("marketing_site/pages/specification_details.jade")
def specification_details(request, pk):
    instrument = get_object_or_404(InstrumentSpecification, pk=pk)
    return {
        "instrument": instrument
    }


# @render_to('contract_specs/trading-calculator.jade')
# def calculator(request):
#     data = Calculator.get_data()
#     context = {'data': json.dumps(data[0]), "exchange_rates": json.dumps(data[1])}
#     return context
def calculator(request):
    return redirect('/')

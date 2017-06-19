# coding: utf-8
from datetime import datetime
import logging

from django.core.cache import cache

from currencies import currencies

log = logging.getLogger(__name__)

cache_key_rate = 'currency.rates.mt4'

__all__ = ["convert_currency"]

MT4_USD_SYMBOLS = (
    "EURUSD",
)


def _get_cache_key(for_date=None):
    if for_date is None:
        return cache_key_rate
    else:
        return cache_key_rate + (str(for_date)[:10]).replace('-', '')


def returns_date(func):
    def inner(*args, **kwargs):
        return_date = kwargs.pop('return_date', None)
        for_date = kwargs.get('for_date')

        res = func(*args, **kwargs)

        res_date = None

        if len(res) > 2:
            amount, from_currency, res_date = res
        else:
            amount, from_currency = res

        if return_date:
            d = datetime.now() if for_date is None else for_date
            return amount, from_currency, res_date or d
        return amount, from_currency
    return inner


@returns_date
def convert_currency(amount, from_currency, to_currency, silent=True, for_date=None, cache_key=None):
    """Convert amount from one currency to another, with caching for old rates
    """
    from_currency = currencies.get_currency(from_currency)
    to_currency = currencies.get_currency(to_currency)

    # пришли некорректные валюты
    if from_currency is None or to_currency is None:
        return None, None

    if amount is None:
        log.error('Recieved ammout for currency convert is None most likely connect to accounts db is broken')

    amount = float(amount)

    if from_currency == to_currency:
        return amount, from_currency

    if amount == 0:
        return 0, to_currency

    if for_date is not None and type(for_date) is datetime:
        for_date = for_date.date()

    return convert_currency_mt4(amount, from_currency, to_currency)

# эта функция не должна вызываться из внешнего кода. следует использовать convert_currency
def convert_currency_mt4(amount, from_currency, to_currency='USD'):
    """Convert amount from one currency to another, no caching"""
    from platforms.mt4.external.models_other import Mt4Quote

    def get_quote(currency):
        if currency.instrument_name == 'BTC':
            quote = Mt4Quote.objects.get(symbol='BTCUSD')
            return Mt4Quote(symbol='USDBTC', ask=1.0 / quote.ask, bid=1.0 / quote.bid)
        return Mt4Quote.objects.get(symbol="USD{}conv".format(currency.instrument_name))

    to_currency = currencies.get_currency(to_currency)
    from_currency = currencies.get_currency(from_currency)

    if to_currency.slug == "USD":
        rate = 1.0 / get_quote(from_currency).ask
    elif from_currency.slug == "USD":
        rate = get_quote(to_currency).bid
    else:
        rate = get_quote(to_currency).bid / get_quote(from_currency).ask

    if rate == 0:
        raise ValueError("Conversion rate cannot be 0")

    return amount * rate, to_currency


def update_mt4_rates(for_date, cache_key):
    """Updates currency rates from MT4 api"""

    api = SocketAPI()

    rates = {}

    for symbol in MT4_USD_SYMBOLS:
        quote = api.quotes_history(symbol=symbol, _from=for_date, _to=for_date,
                                   period="D1")[-1].close
        if symbol.endswith('USD'):
            quote = 1/quote
        rates[symbol.replace('USD', '').replace('conv', '')] = quote

    rates['USD'] = 1.
    # rates['RUB'] = rates['RUR']
    rates['for_date'] = for_date

    cache.set(cache_key, rates, 43200)  # timeout is 12 hours

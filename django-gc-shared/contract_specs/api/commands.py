# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.datastructures import SortedDict

from platforms.mt4.api import SocketCommand


def str_to_num(string):
    """Try to convert a string to a number"""
    try:
        return float(string)
    except ValueError:
        try:
            return int(string)
        except ValueError:
            return string


class Symbol(SocketCommand):
    command = 'GETSYMBOL'

    def before(self, api, symbol):
        kwargs = SortedDict.fromkeys(('MASTER', 'IP', 'SYMBOL'), '')
        kwargs.update({
            'MASTER': settings.MT4_PLUGIN_CONTRACT_SPECS_PASSWORD,
            'IP': '127.0.0.1',
            'SYMBOL': symbol
        })
        return super(Symbol, self).before(api, **kwargs)

    def after(self, api, result):
        result = dict(v.split('=') for v in result.split('\r\n'))
        result = dict((k, str_to_num(v)) for k, v in result.iteritems())
        return result


Symbol.register('symbol')

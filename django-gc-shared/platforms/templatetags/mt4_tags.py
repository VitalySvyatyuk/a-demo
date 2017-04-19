# -*- coding: utf-8 -*-

from django.template import Library
from django.template.defaultfilters import floatformat

from platforms.types import *
from platforms.models import TradingAccount


register = Library()


@register.simple_tag
def get_balance(mt4_id):
    try:
        mt4_id = int(mt4_id)
        balance = TradingAccount(mt4_id=mt4_id).balance
    except:
        balance = ""
    return floatformat(str(balance), arg=2)


@register.simple_tag
def min_deposit(account_type):
    """ Command example:
                        'demo.ss'  --> SSDemoStandardAccountType.min_deposit
                        'ss'       --> SSStandardAccountType.min_deposit
                        'demo'     --> DemoStandardAccountType.min_deposit
    """
    command = account_type.lower().split('.')

    if 'demo' in command:
        if 'ss' in command:
            return unicode(SSDemoStandardAccountType.min_deposit)
        elif 'cfh' in command:
            return unicode(CFHDemoStandardAccountType.min_deposit)
        else:
            return unicode(DemoStandardAccountType.min_deposit)
    else:
        if 'ss' in command:
            return unicode(SSStandardAccountType.min_deposit)
        elif 'cfh' in command:
            return unicode(CFHStandardAccountType.min_deposit)
        else:
            return unicode(StandardAccountType.min_deposit)

    # return unicode(StandardAccountType.min_deposit)

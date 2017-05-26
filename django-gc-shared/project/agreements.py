# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

AGREEMENTS = {

    ###
    # COMMON
    ###

    'client_agreement': {
        "label": _('Client agreement'),

        "default": '/static/agreements/Customer_Agreement.pdf',
        "order": 40,
    },
    'risk_disclosure': {
        "label": _('Risk disclosure'),
        "default": '/static/agreements/Risk_Disclosure.pdf',
        "order": 10,
    },
    'statement_trade_ops': {
        "label": _('Regulation of trades'),

        "default": '/static/agreements/Regulation_of_Trades.pdf',
        "order": 60,
    },
    'pm_agreement': {
        "label": _('PM Agreement'),

        "default": '/static/agreements/PM_Agreement.pdf',
        "order": 60,
    },

    ###
    # REAL IB
    ###
    'real_ib_partner': {
        "label": _(u'Partner agreement'),

        "default": '/static/agreements/Partner_Agreement.pdf',

        "order": 120,
    },
}

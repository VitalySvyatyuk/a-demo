# -*- coding: utf-8 -*-
default_app_config = 'payments.apps.PaymentsConfig'

from itertools import chain

from django.utils.translation import ugettext_lazy as _
from shared.utils import define

# Arum Capital bank accounts
define('BANKS', {
    "Verso": (
        (_("Beneficiary"), "ARUMPRO CAPITAL LIMITED"),  # Получатель
        (_("Beneficiary Bank"), "RCB Bank Ltd"),  # Банк получателя
        (_("Beneficiary Bank's Code"), "RCBLCY21"),  # Код банка получателя
        (_("Beneficiary Bank's Address"), _("2, Amathountos street, P.O. Box 56868, 3310, Limassol, Cyprus")),  # Адрес банка получателя
        (_("Beneficiaries Account Number"), "CY29126000000000000036574004"),  # Номер счета получателя
        (_("Payment Reference"), _("Top UP of the trading AC")), # Назначение платежа
    ),
})

PAYMENT_SYSTEMS_FORMS = {
    "quick": ["accentpay", "accentpay_cards", "accentpay_comepay", "accentpay_sberbank",
              "accentpay_terminal", "accentpay_yandex"],
    "phone": ["accentpay_qiwi"],
    "transfer": ["westernunion", "moneygram"],
    "preview": ["bankrur", "bankeur", "bankusd"],
}


PAYMENT_SYSTEM_TYPES = {
    "deposit": {
        "bank": {
            "systems": ["bankusd"],
            "title": _("Bank transfer"),
            "slug": "bank",
            "order": 10
        },
        # "card": {
        #     "systems": ["accentpay_cards"],
        #     "title": _("Payment card"),
        #     "order": 20
        # },
        # "mobile": {
        #     "systems": [],
        #     "title": u"Мобильный телефон",
        #     "order": 40
        # },
        "electronic": {
            "systems": ['ecommpay', "neteller", "moneybookers"],
            "title": _("Electronic payment systems"),
            "order": 60
        },
        # "terminal": {
        #     "systems": ["accentpay_terminal"],
        #     "title": u"Терминал оплаты",
        #     "order": 70
        # },
        # "transfer": {
        #     "systems": [],
        #     "title": _("Money order"),
        #     "order": 50
        # },
        # "onlinebank": {
        #     "systems": ["accentpay_sberbank"],
        #     "title": _("Online banking"),
        #     "order": 30
        # }

    },
    "withdraw": {
        "bank": {
            "systems": ["bankusd"],
            "title": _("Bank transfer"),
            "order": 10
        },
        "electronic": {
            "systems": ["neteller", "moneybookers", "ecommpay"],
            "title": _("Electronic payment systems"),
            "order": 20
        },
        # "transfer": {
        #     "systems": ["forsazh"],
        #     "title": _("Money order"),
        #     "order": 30
        # },
    },
}

PAYMENT_SYSTEMS_REVERSED = set(chain(*[
    t["systems"]
    for operation, types in PAYMENT_SYSTEM_TYPES.items()
    for t in types.values()
]))

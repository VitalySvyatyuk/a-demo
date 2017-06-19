# -*- coding: utf-8 -*-
"""
Generic Platform Exception.
"""


class PlatformError(Exception):
    # error codes
    REPEATED_PAYMENT = 0  # попытка повторного платежа; ок
    NOT_ENOUGH_MONEY = 11  # на счете недостаточно денег для проведения операции

    code = 0
    message = "OK"

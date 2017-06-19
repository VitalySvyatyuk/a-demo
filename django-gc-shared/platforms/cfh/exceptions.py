# -*- coding: utf-8 -*-
"""
CFH Webservice Exception.
"""
from platforms.exceptions import PlatformError


class CFHError(PlatformError):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message
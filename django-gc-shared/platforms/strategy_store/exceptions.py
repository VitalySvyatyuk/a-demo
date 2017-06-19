# -*- coding: utf-8 -*-
"""
Strategy Store Webservice Exception.
"""
from platforms.exceptions import PlatformError


class SSError(PlatformError):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return self.message
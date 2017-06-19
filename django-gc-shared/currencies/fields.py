# -*- coding: utf-8 -*-

from django.db import models
from currencies import get_currency


class CurrencyField(models.CharField):

    description = "Currency field"
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 6
        super(CurrencyField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, CurrencyField):
            return value
        return get_currency(value)

    def get_prep_value(self, value):
        if isinstance(value, basestring):
            return value
        return value.slug

# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from logging import getLogger

from payments.utils import load_payment_system, PaymentSystemProxy

log = getLogger(__name__)


class PaymentSystemField(models.CharField):
    __metaclass__ = models.SubfieldBase

    description = "Field, holding a reference to the payment system module."

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 50
        super(PaymentSystemField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, list):
            return map(self._to_python, value)
        return self._to_python(value)

    def _to_python(self, value):
        if (isinstance(value, PaymentSystemProxy) and
            hasattr(value, "name") and hasattr(value, "slug")):
            return value

        try:
            # This is more of a hack right now, since we have payment
            # systems organized into three separate lists for each type
            # of operations permitted, and we don't have the operation
            # on the field level.
            value = load_payment_system(value)
        except ImproperlyConfigured as e:
            log.error("Failed to pytonize value: %s of %s" % (value, type(value)))
            log.exception(e)
            value = super(PaymentSystemField, self).to_python(value)
        finally:
            return value

    def get_prep_value(self, value):
        if (isinstance(value, PaymentSystemProxy) and
            hasattr(value, "name") and hasattr(value, "slug")):
            return value.slug

        return super(PaymentSystemField, self).get_prep_value(value)

    def get_prep_lookup(self, lookup_type, value):
        return super(PaymentSystemField,
                     self).get_prep_lookup(lookup_type, self.to_python(value))

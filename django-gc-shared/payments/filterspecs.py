# -*- coding: utf-8 -*-

from django.contrib.admin import AllValuesFieldListFilter
from django.core.exceptions import ImproperlyConfigured

from payments.utils import load_payment_system


class PaymentSystemFilter(AllValuesFieldListFilter):
    def __init__(self, field, request, params, model, model_admin, **kwargs):
        # This sucks, but it looks like there's no other choice to
        # extract operation.
        self.operation = {
            "depositrequest": "deposit",
            "withdrawrequest": "withdraw",
            "userrequisit": "link"}[model.__name__.lower()]
        super(PaymentSystemFilter,
              self).__init__(field, request, params, model, model_admin, **kwargs)

    def title(self):
        # Not localized, but at least this is proper russian :)
        return u"платежной системе"

    def choices(self, cl):
        choices = super(PaymentSystemFilter, self).choices(cl)
        yield choices.next()  # Leaving "All" unchanged.

        while True:
            choice = choices.next()
            try:
                choice["display"] = load_payment_system(choice["display"])
            except (KeyError, ImproperlyConfigured):
                choice["display"] = "Invalid system"
            yield choice

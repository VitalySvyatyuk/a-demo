# -*- coding: utf-8 -*-

from django.dispatch import Signal

account_created = Signal(providing_args=["type_details", "mt4data"])

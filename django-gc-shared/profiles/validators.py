# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from platforms.models import TradingAccount



def is_partner_account(value):
    if value:
        try:
            TradingAccount.objects.real_ib().get(mt4_id=value)
        except (TradingAccount.DoesNotExist, ValueError):
            raise ValidationError(_("Wrong partner code"))
        except TradingAccount.MultipleObjectsReturned:
            pass
    return True


latin_chars_name = RegexValidator(
    regex=r'^[a-zA-Z ,.\'\-]*$',
    message=_("Please use latin-based characters only"),
    code='invalid_name')

latin_chars_name_with_numbers = RegexValidator(
    regex=r'^[a-zA-Z ,.\'\-#№0-9&\(\)\"\\/]*$',
    message=_("Please use latin-based characters only"),
    code='invalid_name')
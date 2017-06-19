# -*- coding: utf-8 -*-

from django.template import Library
from callback_request.models import CATEGORY_CHOICES

register = Library()


@register.assignment_tag
def callback_request_choices():
    return CATEGORY_CHOICES

# -*- coding: utf-8 -*-

from django import template
from django.template.base import VariableDoesNotExist, FilterExpression
from django.template.defaulttags import token_kwargs
from currencies import currencies


register = template.Library()


class SignedAmountNode(template.Node):
    def __init__(self, amount, currency, extra_context=None):
        self.amount = amount
        self.currency = currency
        self.extra_context = extra_context or {
            'precision': 2
        }

    def render(self, context):
        try:
            amount = self.amount.resolve(context)
        # This happens if the balance cannot be calculated
        except (AttributeError, VariableDoesNotExist):
            return ''
        if amount is None:
            return ''

        currency = self.currency.resolve(context)
        currency = currencies.get_currency(currency)

        precision = self.extra_context['precision']

        if isinstance(precision, FilterExpression):
            precision = precision.var.resolve(context)
        return currency.display_amount(amount, precision=precision)


@register.tag
def signed_amount(parser, token):
    """Take a number and currency and display it according to the language

    Examples:
    {% signed_amount 100 'USD' %}
    Shows 100$ in russian and $100 in other languages
    {% signed_amount -100 'EUR' %}
    Shows -100€ in russian language and -€100 in other languages

    It also accepts precision argument, and rounds the value to that precision
    with decimal computations
    {% signed_amount balance account.currency precision=2 %}

    """
    bits = token.split_contents()
    if not 3 <= len(bits) <= 4:
        raise template.TemplateSyntaxError, "%r tag requires 2 arguments" % token.contents.split()[0]

    tag, amount, currency = bits[:3]

    extra_context = token_kwargs(bits[3:], parser)

    amount = template.Variable(amount)
    currency = template.Variable(currency)
    
    return SignedAmountNode(amount, currency, extra_context=extra_context)

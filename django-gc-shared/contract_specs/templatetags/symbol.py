# -*- coding: utf-8 -*-

from django import template
# from django.utils.safestring import mark_safe
# from faq.models import Question
from contract_specs.models import SymbolDescription

register = template.Library()


@register.filter('symbol_link')
def symbol_link(val):
    return val
    # tmpl = '''<a target='blank'
    #              href='/instruments_description/?q={0}'
    #              class="dashed">
    #                 {1}
    #           </a>'''
    # if val is not None and Question.objects.filter(question=val.replace('_OP', '')).exists():
    #     return mark_safe(tmpl.format(val.replace('_OP', ''), val))
    # else:
    #     return val


@register.assignment_tag
def group_description(group):
    description = SymbolDescription.objects.filter(type='instrument', symbol=group).first()
    if description:
        return description.description
    return ""

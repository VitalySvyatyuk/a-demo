__author__ = 'abazhko'

from django.template import Library
from django.utils.safestring import mark_safe
from django.template import Template
from node.models import Node

register = Library()

@register.simple_tag(takes_context=True)
def node_content(context, node):
    t = Template(mark_safe(node.body))
    try:
        return t.render(context)
    except:
        return mark_safe(node.body)


@register.simple_tag
def node_url(node_id):
    try:
        return Node.objects.get(id=node_id).get_absolute_url()
    except :
        return ''
# -*- coding: utf-8 -*-

from django import template
from django.template.defaulttags import url

from treemenus.models import Menu, MenuItem
from treemenus.config import APP_LABEL


def show_menu(context, menu_name, menu_type=None):
    try:
        menu = Menu.objects.get(name=menu_name)
        menu.root_item.set_children(context["request"])
    except Exception: # Formely Menu.DoesNotExist.
        menu = None
    finally:
        context["menu"] = menu

    if menu_type:
        context["menu_type"] = menu_type

    return context

def show_menu_item(context, menu_item):
    if not isinstance(menu_item, MenuItem):
        raise template.TemplateSyntaxError(
            "Given argument must be a MenuItem object.")

    context['menu_item'] = menu_item
    return context


class ReverseNamedURLNode(template.Node):
    def __init__(self, named_url, parser):
        self.named_url = named_url
        self.parser = parser

    def render(self, context):
        from django.template import TOKEN_BLOCK, Token

        resolved_named_url = self.named_url.resolve(context)
        contents = u'url ' + resolved_named_url

        urlNode = url(self.parser, Token(token_type=TOKEN_BLOCK, contents=contents))
        return urlNode.render(context)


def reverse_named_url(parser, token):
    bits = token.contents.split(' ', 2)
    if len(bits) !=2 :
        raise template.TemplateSyntaxError(
            "'%s' takes only one argument (named url)" % bits[0])
    named_url = parser.compile_filter(bits[1])

    return ReverseNamedURLNode(named_url, parser)


register = template.Library()
register.tag(reverse_named_url)
register.inclusion_tag('%s/menu.html' % APP_LABEL, takes_context=True)(show_menu)
register.inclusion_tag('%s/menu_item.html' % APP_LABEL, takes_context=True)(show_menu_item)

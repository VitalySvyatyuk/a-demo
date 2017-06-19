import re

from django import template
from django.template.defaultfilters import stringfilter
from shared.utils import sanitize_html


SEVERAL_BR_RE = re.compile('(?m)(<br\s*(>|/>)\s*){3,}')
EMPTY_P_TAG_RE = re.compile('(?m)<p>(\s*|\s*&nbsp;?\s*)</p>')
register = template.Library()

@register.filter('lessbr')
def lessbr(content):
    """Replace 3 and more linebreaks with 1"""
    content = SEVERAL_BR_RE.sub('<br/>', content)
    return content

@register.filter('noemptyp')
def noemptyp(content):
    """Replace 3 and more linebreaks with 2"""
    content = EMPTY_P_TAG_RE.sub('', content)
    return content

@register.filter('asaliasclass')
def asaliasclass(content):
    if content == None:
        return ""
    return content.split('/')[-1].replace('.','-')


register.filter("sanitize", stringfilter(sanitize_html))
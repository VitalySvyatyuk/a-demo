# -*- coding: utf-8 -*-

# TODO(Sergei): merge this file with app_tags.py, which should be removed.

import re
from hashlib import md5
import os.path

import random
from django.utils.translation import get_language
from django import template
from django.template import Library, TemplateSyntaxError, Variable, Template
from django.template.defaultfilters import stringfilter
from django.core.cache import cache
from django.conf import settings

from shared.utils import random_media_url
from shared.ad_banners import get_ad_banners

re_newlines = re.compile(r"([\r\n]){3,}")
re_whitespace = re.compile("([\t ]){2,}")

register = Library()


@register.filter
@stringfilter
def compress(value):
    """Filter compresses whitespace characters in a given string.

    >>> compress("iggy\n\n\nrocks!  ")
    'iggy\nrock!'
    >>> compress("iggy\n\n   rocks!")
    'iggy\n\nrocks'
    """
    # a) removing indentation in the begning of the string.
    value = re.sub(r"(?m)^[\t ]+", "", value)

    # b) replacing each two whitespaces with a single one and each
    # __three__ newlines with __two__.
    return re_whitespace.sub("\\1",
                             re_newlines.sub("\\1\\1", value)).strip()


@register.inclusion_tag('flowplayer.html', takes_context=True)
def flowplayer(context, id, src, width=500, height=381,
               img_src='img/education_splash.png'):
    id = ''.join([str(v) for v in (id, width, height,)])
    context.update(locals())
    context.update({'domain': 'https://grandcapital.ru'})
    return context


RU_MONTH_NAMES = {
    1: u'Январь',
    2: u'Февраль',
    3: u'Март',
    4: u'Апрель',
    5: u'Май',
    6: u'Июнь',
    7: u'Июль',
    8: u'Август',
    9: u'Сентябрь',
    10: u'Октябрь',
    11: u'Ноябрь',
    12: u'Декабрь'
}


@register.filter
def ru_month(date):
    return RU_MONTH_NAMES[date.month]


@register.filter
def ru_month_year(date):
    return RU_MONTH_NAMES[date.month] + ' %i' % date.year


@register.inclusion_tag('table_header.html', takes_context=True)
def table_header(context, headers):
    return {
        'headers': headers,
    }


# This dict stores the modification time of static files.
MEDIA_URL_MTIMES = {}


@register.simple_tag
def MEDIA_URL(path=None):
    """Choose a random of media urls.

    Try to find out the modification time of file, and append it to the url.
    The modification time is only checked on first access.
    """

    if not path:
        return random_media_url()

    # Remove leading slashes
    while path.startswith('/'):
        path = path[1:]

    # Remove existing query string
    path = path.split('?')[0]

    # Find the real file modification time, but first try to get it
    # from MEDIA_URL_MTIMES
    filepath = os.path.join(settings.STATIC_ROOT, path)
    if path not in MEDIA_URL_MTIMES:
        try:
            mtime = os.path.getmtime(filepath)
        except (IOError, OSError):
            mtime = None
        MEDIA_URL_MTIMES[path] = mtime
    else:
        mtime = MEDIA_URL_MTIMES[path]

    cache_key = 'media_url.%s' % md5('%s:%s' % (path, mtime)).hexdigest()

    # Do not check the cache if debug is set
    #    if settings.DEBUG or not settings.STATIC_URLS:
    #        url = None
    #    else:
    #        url = cache.get(cache_key)
    #    if url:
    #        return url
    url = '%s%s?v=%s' % (random_media_url(), path, mtime or 1)
    cache.set(cache_key, url)
    return url


@register.simple_tag
def MEDIA_ROOT():
    return settings.STATIC_ROOT


class RenderAsTemplateNode(template.Node):
    def __init__(self, variable):
        self.variable = Variable(variable)

    def render(self, context):
        t = Template(self.variable.resolve(context))
        return t.render(context)


def render_as_template(parser, token):
    bits = list(token.split_contents())
    if len(bits) < 2:
        raise TemplateSyntaxError('%r tag requires at least one argument' % bits[0])
    return RenderAsTemplateNode(bits[1])


render_as_template = register.tag(render_as_template)

# template tag for advantages on left sidebar
@register.inclusion_tag('includes/advantages.html')
def get_random_advantages(use_domain_url=False):
    url = u"http://%s" % (settings.LANGUAGE_SETTINGS[get_language()]["hosts"][0])

    if not use_domain_url:
        url = ""

    ads = get_ad_banners(get_language(), url)
    advantages = random.sample(ads, 5)
    return {'advantages': advantages}


@register.filter
def order_by(query_set, order):
    return query_set.order_by(order)


@register.filter
def percentage(value):
    try:
        return '{0:.2%}'.format(value)
    except ValueError:
        return value


# get list items or paragraphs from the same raw text
@register.filter
def get_list_items(value):
    value = value or ""
    lines = value.splitlines()
    newlines = []

    for l in lines:
            if l.startswith('-'):
                newlines.append(l.strip('-'))

    return newlines


@register.filter
def get_paragraphs(value):
    value = value or ""
    lines = value.splitlines()
    newlines = []
     
    for l in lines:
            if not l.startswith('-'):
                newlines.append(l)

    return newlines
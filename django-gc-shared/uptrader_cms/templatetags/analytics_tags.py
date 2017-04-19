# -*- coding: utf-8 -*-

from django import template

register = template.Library()


@register.simple_tag
def draw_stars(importance):

    stars = [
        '<span class="icon icon-star"></span>',
        '<span class="icon icon-star"></span>',
        '<span class="icon icon-star"></span>',
    ]

    for i in range(importance):
        stars[i] = '<span class="icon icon-star-fill"></span>'

    return "".join(stars)

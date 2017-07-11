# -*- coding: utf-8 -*-
import time
from copy import copy
from difflib import SequenceMatcher
from functools import wraps

from django import forms
from django.conf import settings
from django.contrib.sitemaps import Sitemap as DjangoSitemap
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import six  # Python 3 compatibility
from django.utils.functional import lazy
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _, get_language
from django.views.decorators.cache import cache_page

# добавляет чекбоксы "Я принимаю" на форму
# объект request нужен для построения пути до файла с соглашением
def get_accept_fields(request, agreements, required=True):
    from project.templatetags.app_tags import agreement_url, agreement_label
    fields = {}

    if agreements:
        labels = []
        for slug in agreements:
            filename = agreement_url(slug)
            label = agreement_label(slug)

            filename = request.build_absolute_uri(filename)
            url = u'<a href="%s" target="_blank">%s</a>' % (filename, label)
            labels.append(url)

        field = forms.BooleanField(
            label='', required=required,
            help_text=lazy(mark_safe, six.text_type)(_('I agree with the following terms and conditions:') + u" " + u", ".join(labels))
        )
        field.widget.attrs['class'] = 'checkbox'
        fields['agreements'] = field
    return fields


def show_differences(left, right):
    match = SequenceMatcher(None, right, left)
    a, b = [], []
    for code, b_from, b_to, a_from, a_to in match.get_opcodes():
        # проходит кортежи, описывающие действия, приводящие строку right к строке left
        a.append("<span class='%s'>%s</span>" % (code, left[a_from:a_to]))
        b.append("<span class='%s'>%s</span>" % (code, right[b_from:b_to]))

    return "".join(a if left else ["None"]), "".join(b if right else ["None"])


# кэширует значения функции для каждого набора значений.
# timeout определяет время кэширования
def memoize(timeout=None):
    cache = {}
    if timeout is None:
        def outer(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                key = args + tuple(kwargs.iteritems())
                if key not in cache:
                    cache[key] = f(*args, **kwargs)
                return cache[key]
            return wrapper
    else:
        def outer(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                import pickle
                key = pickle.dumps(args + tuple(kwargs.iteritems()))
                now = int(time.time())
                if key not in cache or now - cache[key]["added at"] > timeout:
                    cache[key] = {
                        "added at": now,
                        "value": f(*args, **kwargs),
                    }
                return cache[key]["value"]
            return wrapper
    return outer


class StatefullModel(models.Model):
    """
    Model with ability to get differences between DB data and current instance.
        `changes` property gives dict
            "field name" -> (db_value, new_value)
    Warning: saved DB-state(_initial_instance) resets upon save call
    """
    # Note: unfortunately Django doesn't allow extending the Meta
    # class, so we're forced to define this on the model level.
    state_ignore_fields = ()  # Fields to ignore when comparing state.

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """Constructor.

        Saves a copy of the original model, to check an instance for
        differences later on.
        """
        super(StatefullModel, self).__init__(*args, **kwargs)
        self._initial_instance = copy(self)

    def _get_changes(self):
        """Generates a dict of field changes since loaded from the database.

        Returns a mapping of field names to (old, new) value pairs:

        >>> profile.changes
        {'user': (<User: boris>, <User: iggy>)}
        """
        changes = {}
        for field in (field.name for field in self._meta.fields
                      if field.name not in self.state_ignore_fields):
            new = getattr(self, field, None)
            old = getattr(self._initial_instance, field, None)
            if old != new:
                changes[field] = (old, new)
        return changes
    changes = property(_get_changes)

    def save(self, *args, **kwargs):
        result = super(StatefullModel, self).save(*args, **kwargs)
        self._initial_instance = copy(self)
        return result


def get_current_domain(language=None):
    lang = language or get_language()
    lang_settings = settings.LANGUAGE_SETTINGS.get(lang, {"redirect_to": "None"})
    return lang_settings["redirect_to"]


def maybe_ajax(template=None, content_type=None):
    def outer(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            response = func(request, *args, **kwargs)

            if request.is_ajax():
                if isinstance(response, dict) or isinstance(response, list):
                    json_response = JsonResponse(response)
                    json_response['content-length'] = len(json_response.content)
                    return json_response
                return response
            else:
                if not isinstance(response, dict):
                    return response
                tmpl = response.pop('TEMPLATE', template)
                return render_to_response(tmpl, response,
                                          context_instance=RequestContext(request), content_type=content_type)

        return wrapper
    return outer


def is_from_external_source(request):
    referer = request.META.get('HTTP_REFERER', None)
    if not referer:  # Allow offices to set regional page as home page for browser
        return True
    if not referer.startswith('http'):
        return False
    for host in settings.ALLOWED_HOSTS:
        if host in referer:
            return False
    return True


class queryset_post_processor(object):
    WHITELIST = ['all', 'filter', 'exclude', 'order_by', 'select_related', 'prefetch_related']

    def __init__(self, qs):
        self.qs = qs

    def __call__(self, func):
        self.func = func
        return self

    def __getitem__(self, item):
        self.qs = self.qs.__getitem__(item)
        return self

    def __getattr__(self, name):
        if name not in queryset_post_processor.WHITELIST:
            return getattr(self.qs, name)

        method = getattr(self.qs, name)

        def wrapper(*a, **kwa):
            self.qs = method(*a, **kwa)
            return self
        return wrapper

    def __iter__(self):
        return iter(self.func(self.qs))


class queryset_like(object):
    """
    QuerySet emulation for Django REST API.
    Incomplete!
    """
    def __init__(self, model, iterable):
        self.iterable = iterable
        self.model = model

    def order_by(self, field):
        descending = False
        if field[0] == '-':
            descending = True
            field = field[1:]
        return queryset_like(self.model, sorted(self.iterable, lambda x, y: -cmp(x, y) if descending else cmp(x, y),
                             lambda x: getattr(x, field, None)))

    def filter(self, **kwargs):
        # TODO: later
        return self

    def exclude(self, **kwargs):
        return self

    def __add__(self, other):
        assert isinstance(other, queryset_like)
        return queryset_like(self.model, self.iterable + other.iterable)

    def all(self):
        return self

    def __len__(self):
        return len(self.iterable)

    def __getitem__(self, item):
        return self.iterable[item]

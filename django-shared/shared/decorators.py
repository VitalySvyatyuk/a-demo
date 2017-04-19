# -*- coding: utf-8 -*-

import hotshot
import os
import tempfile
import time

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse
import json
from django.utils.encoding import force_unicode
from django.utils.functional import wraps

from hashlib import sha1

PROFILE_LOG_BASE = getattr(settings, "PROFILE_LOG_BASE",
                           tempfile.gettempdir())


def profile(fpath):
    """
    Decorator uses hotshot profiler to profile a callable decorated,
    and dumps profiler data to a given location, which can be either
    relative to `settings.PROFILE_LOG_BASE`, or absolute.

    Note: UTC timestamp is appended to a given filename, so that
    `func.profile` will become `func_20100211T170321.prof`.
    """

    if not os.path.isabs(fpath):
        fpath = os.path.join(PROFILE_LOG_BASE, fpath)

    def decorator(func):
        def inner(*args, **kwargs):
            fname, fext = os.path.splitext(fpath)
            profile = hotshot.Profile(
                "%s_%s%s" % (fname,
                             time.strftime("%Y%m%dT%H%M%S", time.gmtime()),
                             fext))

            try:
                result = profile.runcall(func, *args, **kwargs)
            finally:
                profile.close()

            return result
        return inner
    return decorator

def cached_func(cache_timeout=900):
    """Cache the result of a function call for the specified number of
    seconds, using Django's caching mechanism. Assumes that the function
    never returns None (as the cache returns None to indicate a miss),
    and that the function's result only depends on its parameters.

    Note: ordering of parameters is important, those calls will be cached
    seprately:

        >>> func(x=1, y=2)
        ...
        >>> func(y=2, x=1)
        ...
        >>> func(1, 2)
        ...

    Usage:

        @cached_func(600)
        def my_expensive_method(arg, ...):
            return expensive_result
    """
    def decorator(func):
        def inner(*args, **kwargs):
            bits = (func.__module__, func.__name__, args, kwargs)
            cache_key = sha1(
                u"".join(unicode(bit) for bit in bits)).hexdigest()

            result = cache.get(cache_key)
            if result is None:
                result = func(*args, **kwargs)
                cache.set(cache_key, result, cache_timeout)
            return result
        return inner
    return decorator

def as_json(func):
    @wraps(func)
    def inner(*args, **kwargs):
        result = func(*args, **kwargs)

        try:
            result, status_code = result if isinstance(result, tuple) else \
                                  ()  # HACK: lists shouldn't be split.
        except (TypeError, ValueError):
            status_code = 200
        finally:
            status = "ok" if status_code == 200 else "error"

        return HttpResponse(json.dumps({"payload": result,
                                        "status": status},
                                         default=force_unicode),
                            # Note: not really usefull, since jQuery doesn't
                            # provide an API for easily accessing parsed XHR
                            # body, in case of a non-200 status.
                            # status=status_code,
                            content_type="application/json")
    return inner

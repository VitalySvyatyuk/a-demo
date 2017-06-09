# coding=utf-8
from django.core.cache import cache


def cache_setdefault(key, default_callable, timeout=None):
    from_cache = cache.get(key)
    if from_cache:
        return from_cache
    kwargs = {'timeout': timeout} if timeout is not None else {}
    default_result = default_callable()
    cache.set(key, default_result, **kwargs)
    return default_result
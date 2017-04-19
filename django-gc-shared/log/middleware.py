# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division


from threading import local

_threadlocals = local()


def get_current_request():
    return getattr(_threadlocals, 'request', None)


class LogMiddleware(object):
    """Middleware that puts the request object in thread local storage."""

    def process_request(self, request):
        _threadlocals.request = request

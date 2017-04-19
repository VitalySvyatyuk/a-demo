# -*- coding: utf-8 -*-
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponseRedirect


class XForwardedForMiddleware():
    def process_request(self, request):
        # gunicorn doesn't set REMOTE_ADDR when working through UNIX socket
        if 'HTTP_X_REAL_IP' in request.META and not request.META['REMOTE_ADDR']:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']
        return None


class PersistNextMiddleware(object):
    """Middleware persists next value in the user's session ...

    ... and redirects the user to the persisted resource right
    after the user authenticates.
    """

    def process_request(self, request):
        #if "next" in request.GET and "next" not in request.session:
        if "next" in request.GET:
            request.session["next"] = request.GET["next"]

    def process_response(self, request, response):
        try:
            if request.user.is_authenticated() and "next" in request.session:
                response = HttpResponseRedirect(request.session.pop("next"))
        finally:
            return response


class ExceptionUserInfoMiddleware(object):
    """
    Adds user details to request context on receiving an exception, so that they show up in the error emails.

    Add to settings.MIDDLEWARE_CLASSES and keep it outermost(i.e. on top if possible). This allows
    it to catch exceptions in other middlewares as well.
    """

    def process_exception(self, request, exception):
        """
        Process the exception.

        :Parameters:
           - `request`: request that caused the exception
           - `exception`: actual exception being raised
        """

        try:
            if request.user.is_authenticated():
                request.META['USERNAME'] = str(request.user.username)
                request.META['USER_EMAIL'] = str(request.user.email)
        except:
            pass


class HeaderSessionMiddleware(SessionMiddleware):
    def process_request(self, request):
        session_key = request.META.get('HTTP_X_SESSION_ID')
        if session_key:
            request.session = self.SessionStore(session_key)
            request.header_session = True

    def process_response(self, request, response):
        return response

from views import node
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.middleware.csrf import CsrfViewMiddleware

class NodeUrlAliasMiddleware(object):
    def process_response(self, request, response):
        if response.status_code != 404:
            return response # No need to check for a node for non-404 responses.

        csrf_middleware = CsrfViewMiddleware()
        csrf_middleware.process_view(request, node, None, None)

        try:
            return node(request)
        # Return the original response if any errors happened. Because this
        # is a middleware, we can't assume the errors will be caught elsewhere.
        except Http404:
            referrer = request.META.get('HTTP_REFERER')
            try:
                if referrer and referrer.endswith(request.path_info):
                    # Seems like the visitor just changed his language. Even if that's not so, there's no point
                    # in viewing the same 404 error page twice, you'll better go see the root :)
                    if '/my/' in request.path:
                        return HttpResponseRedirect("/my/")
                    return HttpResponseRedirect("/")
            except UnicodeDecodeError:
                return response
            return response
        except:
            if settings.DEBUG:
                raise
            return response
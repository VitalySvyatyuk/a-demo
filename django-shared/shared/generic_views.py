from django.utils.translation import get_language
from django.views.generic import ListView as DjangoListView, TemplateView as DjangoTemplateView,\
                                 RedirectView as DjangoRedirectView, DetailView as DjangoDetailView
from django.views.generic.base import ContextMixin


class ExtraContextMixin(ContextMixin):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        if callable(self.extra_context):
            context.update(self.extra_context())
        else:
            context.update(self.extra_context)
        return context


class PostAllowedMixin(object):
    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)


class ListView(DjangoListView, ExtraContextMixin, PostAllowedMixin):
    pass


class TemplateView(DjangoTemplateView, ExtraContextMixin, PostAllowedMixin):
    pass


class DetailView(DjangoDetailView, ExtraContextMixin, PostAllowedMixin):
    def __init__(self, **kwargs):
        if not self.model:
            self.model = kwargs.pop('model')
        super(DetailView, self).__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        obj = kwargs.get('object')
        if obj and hasattr(obj, "get_context_values"):
            context.update(obj.get_context_values())
        return context


class NodeDetailView(DetailView):
    """
    A special DetailView for Node-based models which can have same slugs etc.
    for different languages
    """
    def get_queryset(self):
        queryset = super(NodeDetailView, self).get_queryset().filter(language=get_language())
        if not (self.request.user.is_authenticated() and self.request.user.is_staff):
            queryset = queryset.filter(published=True)
        return queryset


class RedirectView(DjangoRedirectView):
    """
    Fixes a bug in Django which doesn't allow unicode characters in query string.
    """

    def get_redirect_url(self, **kwargs):
        """
        Return the URL redirect to. Keyword arguments from the
        URL pattern match generating the redirect request
        are provided as kwargs to this method.
        """
        if self.url:
            url = self.url % kwargs
            # GC PATCH: We will get args as a QueryDict instance and urlencode it properly
            args = self.request.GET
            if args and self.query_string:
                url = "%s?%s" % (url, args.urlencode())
            return url
        else:
            return None

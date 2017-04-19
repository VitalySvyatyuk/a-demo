# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.http.response import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.utils.translation import get_language
from node.models import Node


def node(request, node_id=None, allowed_hidden_classes=None):
    """
    Gets node by ID or by request path

    Optionally pass a list of models which are allowed to be shown in spite of being set up as hidden
    """
    language = get_language()
    if not node_id:
        url = request.path_info[1:]

        q = Q(url_alias__exact=url)

        if url.endswith("/"):
            q |= Q(url_alias__exact=url.strip("/"))
        else:
            q |= Q(url_alias__exact=url + "/")

        node = get_object_or_404(Node, q, language=language, published=True)

        if node.url_alias != url:
            args = request.META.get('QUERY_STRING', '')
            if args:
                node.url_alias += "?%s" % args
            domain = settings.LANGUAGE_SETTINGS[language]["redirect_to"]
            return HttpResponsePermanentRedirect(domain + "/" + node.url_alias)
    else:
        node = get_object_or_404(Node, id=node_id, language=language)
    node = node.as_leaf_class()
    if node.hide and (allowed_hidden_classes is None or type(node) not in allowed_hidden_classes):
        raise Http404()
    if not node.public_access:
        if not request.user.is_authenticated():
            return redirect('auth_login')
        if not node.has_access(request.user):
            return HttpResponseForbidden()
    if hasattr(node, "check_access") and not node.check_access(request.user):
        return HttpResponseForbidden()
    if request.is_ajax():
        return HttpResponse(node.render())

    context = {'node': node}
    context.update(node.get_context_values())
    return render_to_response(node.get_template_name(request), context,
                              context_instance=RequestContext(request))

from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request
from djangobb_forum.util import render_to

from treemenus.models import MenuItem,Menu


@ajax_request
def reorder(request):
    """Reorder treemenus, call from ajax"""
    if not request.user.has_perm('tremenus.change_menuitem'):
        return HttpResponseForbidden()
    try:
        parent_id = int(request.GET['parent'])
        children = map(int, request.GET['order'].split(','))
    except (KeyError, ValueError), e:
        return HttpResponseBadRequest()
    parent = get_object_or_404(MenuItem, pk=parent_id)

    ranks = dict((v,k) for k, v in enumerate(children))

    for item in MenuItem.objects.filter(parent=parent, pk__in=children):
        try:
            item.rank = ranks[item.pk]
        except KeyError:
            # This should not have happened
            continue
        # Override default save method
        super(MenuItem, item).save()
    return {'payload': True}


@render_to('treemenus/menu_map.html')
def menumap(request,menu_name):
    menu = get_object_or_404(Menu,name=menu_name)
    return {'menu':menu}
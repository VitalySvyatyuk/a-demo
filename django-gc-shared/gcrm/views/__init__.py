# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from annoying.decorators import render_to
from django.shortcuts import render
from django.http import Http404
from crm.models import PersonalManager
from django.contrib.auth.decorators import login_required
from gcrm.models import Task


@login_required
@render_to('gcrm/app.html')
def app(request):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    if not request.user.crm_manager or not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        raise Http404()
    return {'task_types': Task.TASK_TYPES}


@login_required
def render_template(request, name):
    if not (request.user.is_superuser or PersonalManager.objects.filter(user=request.user).exists()):
        raise Http404()
    if not request.user.crm_manager or not request.user.crm_manager.is_ip_allowed(request.META['REMOTE_ADDR']):
        raise Http404()
    return render(request, "gcrm/js/{name}.html".format(name=name))

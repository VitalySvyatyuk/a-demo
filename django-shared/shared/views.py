# -*- coding: utf-8 -*-
from __future__ import with_statement
from datetime import datetime, date, time, timedelta
import mimetypes
import urlparse

import re
import os
import stat
import os.path

from django.http import HttpResponseBadRequest, Http404, HttpResponse, \
    HttpResponseNotModified, HttpResponseForbidden
from django.conf import settings
from django.views.static import was_modified_since
from django.utils.http import http_date
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request

from shared.models import VideoStat
from shared.utils import random_media_url


@ajax_request
def video_view_count(request):
    url = request.GET.get('url')
    if not url:
        return HttpResponseBadRequest()
    if request.user.is_authenticated():
        user = request.user
    else:
        user = None
    VideoStat.objects.create(user=user, videofile=url)
    return {'payload': True}


@login_required
@ajax_request
@require_POST
def easy_comments_update(request):
    module_name = request.POST.get('module')
    model_name = request.POST.get('model')
    model_pk = request.POST.get('pk')
    if not (module_name and model_name and model_pk):
        raise Http404

    public_comment_field = request.POST.get('public_comments_field')
    private_comment_field = request.POST.get('private_comments_field')

    module = __import__(module_name, locals(), globals(), [model_name], -1)
    model = getattr(module, model_name)
    app_name = model._meta.app_label

    if not request.user.has_perm('%s.change_%s' % (app_name, model_name.lower())):
        return HttpResponseForbidden()

    obj = get_object_or_404(model, pk=model_pk)

    if public_comment_field:
        setattr(obj, public_comment_field, request.POST.get('public_comment', ''))

    if private_comment_field:
        setattr(obj, private_comment_field, request.POST.get('private_comment', ''))

    obj.save()
    return {}
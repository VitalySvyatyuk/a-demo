# -*- coding: utf-8 -*-

from annoying.decorators import render_to
from callback_request.forms import CallbackForm
from django.shortcuts import redirect
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseBadRequest
from json import dumps

def callback_request(request):
    form = CallbackForm(request.POST or None)
    if form.is_valid():
        form.save()
        phone_number = form.cleaned_data.get('phone_number')
        category = form.cleaned_data.get('category')
        time_start = form.cleaned_data.get('time_start')
        time_end = form.cleaned_data.get('time_end')
        name = form.cleaned_data.get('name')
        comment = form.cleaned_data.get('comment')
        time_of_day = form.cleaned_data.get('time_of_day')

        send_mail(
            u"Application for callback recieved",
            u'Name: {} requestes callback\nQuestion category: {},\nSuit time: {} - {} ({})\n'
            u'Phone: {}\nUser comment: {}'.
                format(name, category, time_start, time_end, time_of_day, phone_number, comment),
            settings.SERVER_EMAIL,
            settings.MANAGERS[0]  # Which means support email
        )
        return HttpResponse(dumps({'result': 'ok'}), content_type='application/json')
    else:
        return HttpResponseBadRequest(dumps({'result': 'error'}), content_type='application/json')

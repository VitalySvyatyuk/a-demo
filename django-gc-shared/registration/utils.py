# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division

from django.contrib.auth.models import User


def generate_username_from_email(email):
    username = email.split('@')[0]
    if User.objects.filter(username=username).exists():
        i = 1
        while True:
            new_username = username + u"_" + unicode(i)
            if User.objects.filter(username=new_username).exists():
                i += 1
            else:
                return new_username
    return username

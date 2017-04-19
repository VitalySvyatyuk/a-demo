# coding=utf-8
from django.conf import settings


def language_settings(request):
    return {
        'LANGUAGE_SETTINGS': settings.LANGUAGE_SETTINGS,
    }
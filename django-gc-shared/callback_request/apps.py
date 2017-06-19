# -*- coding: utf-8 -*-

from django.apps import AppConfig


class CallbackRequestConfig(AppConfig):
    name = 'callback_request'

    def ready(self):
        from notification.models import NotificationTypesRegister

        NotificationTypesRegister.register_notification('callback_request', u'Callback request')

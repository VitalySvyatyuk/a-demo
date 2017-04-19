# coding=utf-8
from django.apps import AppConfig


class TransfersConfig(AppConfig):
    name = 'transfers'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('manual_transfer_submitted', u'Internal transfer issue created')

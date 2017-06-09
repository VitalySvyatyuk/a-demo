# coding=utf-8
from django.apps import AppConfig


class PrivateMessagesConfig(AppConfig):
    name = 'private_messages'

    def ready(self):
        from notification.models import NotificationTypesRegister


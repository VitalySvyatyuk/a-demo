# coding=utf-8
from django.apps import AppConfig


class ReportsConfig(AppConfig):
    name = 'reports'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('report_generation_failed', u'Report generation failed')
        NotificationTypesRegister.register_notification('report_has_been_generated', u'Report generation finished')

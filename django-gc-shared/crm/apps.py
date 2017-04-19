# coding=utf-8
from django.apps import AppConfig


class CrmConfig(AppConfig):
    name = 'crm'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('crm_reassignrequest_accepted', '', app_name=self.name)
        NotificationTypesRegister.register_notification('crm_reassignrequest_rejected', '', app_name=self.name)
        NotificationTypesRegister.register_notification('crm_reassignrequest_new', '', app_name=self.name)

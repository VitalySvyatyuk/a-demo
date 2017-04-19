# coding=utf-8
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class RegistrationConfig(AppConfig):
    name = 'registration'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('user_registered', _('User registered'),
                                                        app_name=self.name)
        NotificationTypesRegister.register_notification('Password_changed', _('Password successfully changed'),
                                                        app_name=self.name)
        # NotificationTypesRegister.register_notification('user_verified', _('User verified'),
        #                                                 app_name=self.name)


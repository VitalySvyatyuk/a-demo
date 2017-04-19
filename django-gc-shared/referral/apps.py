# coding=utf-8
from django.apps import AppConfig


class ReferralConfig(AppConfig):
    name = 'referral'

    def ready(self):
        from notification.models import NotificationTypesRegister
        # NotificationTypesRegister.register_notification('partnercertificate_issue', u'')
        # NotificationTypesRegister.register_notification('referral_account_created', u'Реферальный счет создан')

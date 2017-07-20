# coding=utf-8
from django.apps import AppConfig


class IssuetrackerConfig(AppConfig):
    name = 'issuetracker'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('account_unblock', u'Account unblock')
        NotificationTypesRegister.register_notification('account_unblock_rejected', u'Account unblock rejected')
        NotificationTypesRegister.register_notification('checkdocument_issue', u'Checking documents')
        NotificationTypesRegister.register_notification('internaltransfer_issue', u'Internal transfer done')
        NotificationTypesRegister.register_notification('internaltransfer_reject', u'Internal transfer rejected')
        NotificationTypesRegister.register_notification('user_issue', u'Support request')
        NotificationTypesRegister.register_notification('document_verified', u'Document verified')
        NotificationTypesRegister.register_notification('documen_rejected', u'Documents rejected')
        NotificationTypesRegister.register_notification('invest_approved', u'Approved possibility to open Invest accounts')

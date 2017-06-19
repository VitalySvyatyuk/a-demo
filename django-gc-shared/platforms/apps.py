# coding=utf-8
from django.apps import AppConfig


class PlatformsConfig(AppConfig):
    name = 'platforms'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('account_created', u'Account created')
        NotificationTypesRegister.register_notification('leverage_change', u'Leverage changed')
        NotificationTypesRegister.register_notification('password_recovery', u'Password recovered')
        NotificationTypesRegister.register_notification('realib_account_created', u'real IB account created')
        NotificationTypesRegister.register_notification('real_pro_account_created', u'real ECN.PRO account created')
        NotificationTypesRegister.register_notification('real_MT_account_created', u'real MT4 account created')
        NotificationTypesRegister.register_notification('real_invest_account_created', u'real ECN.Invest account created')
        NotificationTypesRegister.register_notification('demo_pro_account_created', u'demo ECN.PRO account created')
        NotificationTypesRegister.register_notification('demo_MT_account_created', u'demo MT4 account created')
        NotificationTypesRegister.register_notification('demo_invest_account_created', u'demo ECN.Invest account created')
        NotificationTypesRegister.register_notification('apllication_for_invest_created', u'Application for open ECN.Invest account')


        import platforms.signals

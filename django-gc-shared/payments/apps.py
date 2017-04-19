# coding=utf-8
from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = 'payments'

    def ready(self):
        import payments.models
        from project.modeltranslate import model_translate
        payments.models.PaymentCategory = model_translate(
            'name'
        )(payments.models.PaymentCategory)
        payments.models.PaymentMethod = model_translate(
            'name', 'commission', 'processing_times', 'link'
        )(payments.models.PaymentMethod)

        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('deposit_needs_verification',
                                                        u'Deposit need verification')
        NotificationTypesRegister.register_notification('deposit_request_committed',
                                                        u'Deposit request committed')
        NotificationTypesRegister.register_notification('deposit_request_created',
                                                        u'Deposit request created')
        NotificationTypesRegister.register_notification('deposit_request_failed',
                                                        u'Deposit request failed')
        NotificationTypesRegister.register_notification('withdraw_processing_in_finance',
                                                        u'Withdraw processing in finance')
        NotificationTypesRegister.register_notification('withdraw_processing_transfer_ready',
                                                        u'Withdraw processing transfer ready')
        NotificationTypesRegister.register_notification('withdraw_processing_verified',
                                                        u'Withdraw processing verified')
        NotificationTypesRegister.register_notification('withdraw_request_committed',
                                                        u'Withdraw request committed')
        NotificationTypesRegister.register_notification('withdraw_request_created',
                                                        u'Withdraw request created')
        NotificationTypesRegister.register_notification('withdraw_request_failed',
                                                        u'Withdraw request failed')

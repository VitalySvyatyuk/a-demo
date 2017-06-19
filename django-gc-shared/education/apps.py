# -*- coding: utf-8 -*-

from django.apps import AppConfig


class EducationConfig(AppConfig):
    name = 'education'

    def ready(self):
        from notification.models import NotificationTypesRegister
        NotificationTypesRegister.register_notification('webinar_2days_reminder', u'2 day until webinar starts')
        NotificationTypesRegister.register_notification('webinar_has_record', u'Webinar has record')
        NotificationTypesRegister.register_notification('webinar_link_to_record_changed',
                                                        u'Webinar link to record changed')
        NotificationTypesRegister.register_notification('webinar_registration', u'Webinar registration')
        NotificationTypesRegister.register_notification('webinar_today_reminder', u'Webinar starts today')
